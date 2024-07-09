import streamlit as st
from pymarc import MARCReader, MARCWriter
from io import BytesIO
from legacy_session_state import legacy_session_state
legacy_session_state()

def clean_and_fix_marc_records(infile, outfile):
    reader = MARCReader(infile, to_unicode=True, force_utf8=True, hide_utf8_warnings=False)
    writer = MARCWriter(outfile)

    for record in reader:
        if record:
            control_number = record['001'].data if '001' in record else 'No Control Number'
            print(f"Processing record: {control_number}")

            for field in record.get_fields():
                if field.is_control_field():
                    continue

                print(f"Processing field {field.tag}")
                new_subfields = []
                subfields = field.subfields

                for i in range(0, len(subfields), 2):
                    code = subfields[i]
                    value = subfields[i + 1] if i + 1 < len(subfields) else ''

                    # Remove dangling subfields and empty subfields
                    if isinstance(code, str) and not code.strip():
                        continue
                    if isinstance(value, str) and not value.strip():
                        continue

                    if isinstance(code, str) and code.strip() and isinstance(value, str) and value.strip():
                        print(f"Subfield code: {code}, value: {value}")
                        new_subfields.extend([code, value])

                field.subfields = new_subfields

            # Process the 008 field
            if '008' in record:
                field_008 = record['008'].data
                field_008 = field_008.ljust(40)[:40]
                record['008'].data = field_008

            writer.write(record)

    writer.close(close_fh=False)


def main():
    st.title("MARC Record Cleaner")
    uploaded_file = st.file_uploader("Choose a MARC file", type=['mrc'])

    if uploaded_file is not None:
        processed_file = BytesIO()
        clean_and_fix_marc_records(uploaded_file, processed_file)
        processed_file.seek(0)

        st.download_button(
            label="Download Processed MARC File",
            data=processed_file,
            file_name="processed.mrc",
            mime="application/marc"
        )


if __name__ == "__main__":
    main()
