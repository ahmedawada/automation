# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 15:51:57 2023

@author: awada
"""

import io
import random
from pymarc import MARCReader, Record, Field, MARCWriter
import pandas as pd
import streamlit as st
import re


def clean_marc_file(file_path):
    # Open the input file and create a MARC reader
    if file_path is not None:
        reader = MARCReader(file_path, force_utf8=True)

        # Create a list to store the cleaned records
        cleaned_records = []

        # Iterate over each record in the file
        for record in reader:

            # Remove empty fields
            if record is not None:
                record.remove_fields([field for field in record if not field.value()])

                if '008' in record:
                    field_008 = record['008']
                    # Remove any occurrences of the Record Separator character
                    field_008.data = field_008.data.replace('\x1E', '')
                    # field_008.data = re.sub(pattern, '', field_008.data)


                if not record.get_fields('245'):
                    title = "Title Not Available "
                    record.add_ordered_field(Field(tag='245', indicators=['0', '0'], subfields=['a', title]))

                # Add a random 001 field if one doesn't exist
                if not record.get_fields('001'):
                    control_number = str(random.randint(10000, 10000000))
                    record.add_ordered_field(Field(tag='001', data=control_number))

                if record.leader[9] != 'a':
                    # Add the letter 'a' to the leader to indicate it is UTF-8 encoded
                    record.leader = record.leader[:9] + 'a' + record.leader[10:]

                leader = record.leader

                # fix the leader length if necessary
                correct_length = 24  # the correct length of the MARC leader
                current_length = len(leader)
                if current_length < correct_length:
                    # if the length is too short, pad with spaces
                    leader = leader.ljust(correct_length)
                elif current_length > correct_length:
                    # if the length is too long, truncate
                    leader = leader[:correct_length]


                # set the fixed leader
                record.leader = leader

                # Replace "45 0" in the leader with "4500"
                leader = record.leader
                if "45 0" in leader:
                    leader = leader.replace("45 0", "4500")
                    record.leader = leader


                # Add the cleaned record to the list
                cleaned_records.append(record)


        with io.BytesIO() as output_file:

            writer = MARCWriter(output_file)
            for record in cleaned_records:
                writer.write(record)

            output_file.seek(0)

            return output_file.read()





def extract_to_dataframe(file_path,tagnum):
    # Open the input file and create a MARC reader

    reader = MARCReader(file_path)

    subfield_data = []
    all_keys = set()

    # Iterate over each record in the file
    for record in reader:
        # Get the fields with tag 999

        fields = record.get_fields(tagnum)

        if fields:
            # Iterate over each field with tag 999
            for field in fields:

                subfields = field.subfields_as_dict()
                # Add the record identifier to the subfield data
                subfields['record_identifier'] = record['001'].value()
                # Add the subfield information to the list
                subfield_data.append(subfields)
                all_keys.update(subfields.keys())

    # Create a pandas dataframe from the subfield data
    df = pd.DataFrame(subfield_data)
    df = df.astype(str)
    df = df.replace(r'\']', '', regex=True)
    df.replace(r"\['", '', regex=True,inplace=True)
    df.replace("nan", '', inplace=True)
    df.fillna('',inplace=True)

    return df.to_csv(index=False, sep='\t').encode('utf-8')

