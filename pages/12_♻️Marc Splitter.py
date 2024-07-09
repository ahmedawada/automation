import streamlit as st
import csv
from pymarc import MARCReader
from io import BytesIO, StringIO
from legacy_session_state import legacy_session_state

def process_marc_file(uploaded_file, marc_tag):
    sequence = 1000  # Starting sequence

    # Convert the uploaded file to a BytesIO object
    marc_file = BytesIO(uploaded_file.read())
    reader = MARCReader(marc_file)

    # This will hold all possible dynamic fieldnames we might encounter
    dynamic_fieldnames = set()

    # First, scan through all records to collect all possible fieldnames dynamically
    for record in reader:
        if record is not None and marc_tag in record:
            tags = record.get_fields(marc_tag)
            for tag in tags:
                for subfield in tag:
                    key = f'{marc_tag}${subfield[0]}'
                    dynamic_fieldnames.add(key)

    # Reset the file pointer to the beginning to read records again
    marc_file.seek(0)
    reader = MARCReader(marc_file)

    # Create an in-memory CSV file using StringIO
    output = StringIO()
    # Initialize CSV writer with all possible fieldnames collected
    base_fieldnames = ['Sequence', 'ControlNumber', 'Call050', 'Call090']
    all_fieldnames = base_fieldnames + sorted(dynamic_fieldnames)
    writer = csv.DictWriter(output, fieldnames=all_fieldnames, delimiter='\t')
    writer.writeheader()

    # Process records
    for record in reader:
        if record is not None and str(marc_tag) in record:
            control_number = record['001'].data if '001' in record else 'No Control Number'
            call050 = record['050'].value() if '050' in record else 'No 050'
            call090 = record['090'].value() if '090' in record else 'No 090'

            tags = record.get_fields(marc_tag)
            for tag in tags:
                fields_data = {'Sequence': sequence, 'ControlNumber': control_number,
                               'Call050': call050, 'Call090': call090}
                sequence += 1

                for subfield in tag:
                    key = f'{marc_tag}${subfield[0]}'
                    fields_data[key] = subfield[1]

                # Write the data row to the CSV file
                writer.writerow(fields_data)

    # Get the CSV content from the in-memory file
    output.seek(0)
    return output.getvalue()

def main():
    st.title("MARC Record Splitter")

    uploaded_file = st.file_uploader("Choose a MARC file", type=['mrc'])
    marc_tag = st.text_input("Enter the MARC tag number to process", value='945')

    if uploaded_file is not None and marc_tag:
        processed_file = process_marc_file(uploaded_file, marc_tag)

        st.download_button(
            label="Download Processed TSV File",
            data=processed_file,
            file_name="processed.tsv",
            mime="text/tab-separated-values"
        )

if __name__ == "__main__":
    main()
