# ___________________________________________________ ANSWERS ___________________________________________________
# Q1: How many complete data frames are in your file? | ANSWER: 205
# Q2: How many messages might be corrupt? | ANSWER: 4
# Q3: What is the calendar date of these messages? | ANSWER: 2022-06-11 (YYYY-MM-DD)

#_________________________________________________ CODE EXPLANATION _______________________________________________________________________________________________________
'''
The method used to decode is by using two lists, namely: current_frame, output frame. By reading one byte at a time and appending to the list,
it is ensured that a count is kept of the byte number and by adding the byte_value to the current_frame list, we can easily get the number of
corrupted frames by adding all the indices. The output_frame is used to output the bytes into human-readable format and output into a csv file.
The values of the current_file and output_file are same but when payload, timing bytes are encountered, we perform calculations to convert it into
human readable format and change it in the output_frame. Finally, after all the 26 bytes have been accounted for, we clear current_frame and output_frame
to start the process for the next iteration.

The variables used:-
complete_frames - to count the number of frames that are completed
corrupt_messages - to count any corrupted frames
calendar_date - to add the calendar dates from the decoded messages to the list
combined_byte - to store the combined bytes (from MSB - LSB)
temperature_table - Lookup table
dt_object - to store the datetime, converting to standard date from the decoded message.
'''
#____________________________________________________ START CODE _____________________________________________________________________________________________________

from datetime import datetime

# Define the temperature lookup table
temperature_table = {
    0xA0: 30.0, 0xA1: 30.1, 0xA2: 30.2, 0xA3: 30.3, 0xA4: 30.4, 0xA5: 30.5, 0xA6: 30.6, 0xA7: 30.7,
    0xA8: 30.8, 0xA9: 30.9, 0xAA: 31.0, 0xAB: 31.1, 0xAC: 31.2, 0xAD: 31.3, 0xAE: 31.4, 0xAF: 31.5,
    0xB0: 31.6, 0xB1: 31.7, 0xB2: 31.8, 0xB3: 31.9, 0xB4: 32.0, 0xB5: 32.1, 0xB6: 32.2, 0xB7: 32.3,
    0xB8: 32.4, 0xB9: 32.5, 0xBA: 32.6, 0xBB: 32.7, 0xBC: 32.8, 0xBD: 32.9, 0xBE: 33.0, 0xBF: 33.1,
    0xC0: 33.2, 0xC1: 33.3, 0xC2: 33.4, 0xC3: 33.5, 0xC4: 33.6, 0xC5: 33.7, 0xC6: 33.8, 0xC7: 33.9,
    0xC8: 34.0, 0xC9: 34.1, 0xCA: 34.2, 0xCB: 34.3, 0xCC: 34.4, 0xCD: 34.5, 0xCE: 34.6, 0xCF: 34.7,
    0xD0: 34.8, 0xD1: 34.9, 0xD2: 35.0, 0xD3: 35.1, 0xD4: 35.2, 0xD5: 35.3, 0xD6: 35.4, 0xD7: 35.5,
    0xD8: 35.6, 0xD9: 35.7, 0xDA: 35.8, 0xDB: 35.9, 0xDC: 36.0, 0xDD: 36.1, 0xDE: 36.2, 0xDF: 36.3
}

# Open the binary input file
input_file = open("binaryFileC_81(1).bin", 'rb')
output_file = open("11457797.csv", 'w')

# Initialize variables to track additional questions
complete_frames = 0
corrupt_messages = 0
calendar_date = []

# Read the first byte and loop as long as there is always another byte available
byte = input_file.read(1)
current_frame = [] # To track the byte_values and append it to the list, it restarts after every frame (26 bytes)
output_frame =[] # To output the byte_values into a human readable format and send it to the csv file
# ___________________________________________________ START ITERATION ___________________________________________________
while byte:
    byte_value = int.from_bytes(byte, byteorder='big')  # Convert byte to integer value
    # Start of a new frame
    if len(current_frame) == 0 and byte_value == 126 and byte == b'~': # ASCII code for '~'
        current_frame.append(byte_value) #append the byte value to the list
        output_frame.append('~')
    elif complete_frames != 0 and len(current_frame)==0 and byte_value != 126 and (not byte == b'~'): # To account for the case where the first character/ at start of the frame, provided is corrupt
        current_frame.append(byte_value)
        output_frame.append(0) # Append 0 to the list if '~' not found

    # Continue adding bytes to the current frame
    elif len(current_frame) > 0:
        current_frame.append(byte_value)
        output_frame.append(byte_value)
        if len(current_frame) == 2 and byte_value == 126 and byte == b'~':  # ASCII code for '~'
            output_frame[1] = '~'
        elif len(current_frame) == 2 and byte_value != 126 and (not byte == b'~'):
            output_frame[-1] = 0  # Append 0 to the list if '~' not found

# ___________________________________________________ START OF PAYLOAD BYTES ___________________________________________________

        elif len(current_frame) == 8 and byte == b'P': # If the 8th Byte is 'P', append the character 'P' to the output_frame
            output_frame[7] = 'P'
        elif len(current_frame) == 8 and (not byte == b'P'): # If 'P' is not found, output 0
            output_frame[7] = 0
        #---RPM-VLT-CRT BYTES---
        # For the 10th, 12th and 14th bytes, combine the MSB and LSB to give 16-bit integer 
        # Combine the pair of bytes into a 16-bit integer
        elif len(current_frame) in [10,12]:
            combined_byte = current_frame[-2] << 8 | current_frame[-1] # Shift the MSB by 8 positions and add with LSB to obtain the combined number
            output_frame[-2:] = [combined_byte]
        elif len(current_frame) == 14: # Accounting for the case where the 13th and 14th bytes are signed integers 
            combined_byte= int.from_bytes(bytearray(current_frame[12:14]), 'little', signed= True) #since the CRT bytes are in little endian format and are signed integers
            output_frame[-2:] = [combined_byte] # Appending the new change to output_frame

        # ---MOSFET-CAPACITOR TEMP BYTES---
        elif len(current_frame) in [15,16]:  # Look for the temperature in the lookup table
            if current_frame[-1] in temperature_table:
                output_frame[-1] = temperature_table[current_frame[-1]]
            else:
                output_frame[-1] = 0.0  # Default value if byte is not found in the lookup table

# ___________________________________________________ START OF TIMING BYTES ___________________________________________________

        elif len(current_frame) == 17 and byte == b'T': # If the 17th Byte is 'T', append the character 'T' to the output_frame
            output_frame[-1] = 'T'
        elif len(current_frame) == 17 and (not byte == b'T'): # If 'T' is not found, output 0
            output_frame[-1] = 0
        elif len(current_frame)== 25:
            # Initialize the combined timestamp
            # Combine the bytes into a single 64-bit integer using BYTEARRAY and converting the combined value to integer
            timestamp = int.from_bytes(bytearray(current_frame[17:25]), 'big')
            output_frame[-8:]=[timestamp] # Appending the output frame with the combined value
            timestamp_seconds = timestamp / 10 ** 6 # Since the given timestamp is in microseconds, converting to seconds
            # Convert Unix timestamp to datetime object to get the date 
            # Accounting for a case where the date might be out of range
            try:
                dt_object = datetime.utcfromtimestamp(timestamp_seconds) 
            except ValueError:
                dt_object = 0
            calendar_date.append(dt_object)
        
            
# ___________________________________________________ CHECKSUM ___________________________________________________
        # If the current frame is complete
        elif len(current_frame) == 26:  # Each frame consists of 26 bytes
            complete_frames += 1
            decoded_frame = [str(i) for i in output_frame[2:]]
            output_file.write(str(output_frame[0]) + str(output_frame[1])+','+','.join(decoded_frame) + ',\n') #TO OUTPUT AS A CSV FILE
            
            # Check for potential corruption based on the checksum
            checksum =255- sum(current_frame[:-1]) % 256
            if checksum != current_frame[-1]:
                corrupt_messages += 1
            # Reset the current frame for the next iteration
            current_frame = []
            output_frame = []

    # Get the next byte from the file
    byte = input_file.read(1)
# ___________________________________________________ END OF ITERATIONS ___________________________________________________

print ('calendar date',calendar_date)
print ('corrupt_messages = ', corrupt_messages)
print ('complete_frames = ', complete_frames)
# Must be end of the file so close the file
print("End of file reached")
input_file.close()
output_file.close()
# _________________________________________________________________________________________________________________________

