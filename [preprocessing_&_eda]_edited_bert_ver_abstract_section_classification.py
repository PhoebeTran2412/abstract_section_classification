# -*- coding: utf-8 -*-
"""[PREPROCESSING & EDA] Edited_BERT_Ver_Abstract_Section_Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rN-BfkA5Vc5nMToka_Pyr1q1DtxlXxki

## I. IMPORT LIBRARIES AND ESSENTIAL FUNCTIONS
"""

# Mount Google drive locally
from google.colab import drive
drive.mount('/content/gdrive')

import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras import layers
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

!pip install --quiet tensorflow-text
!pip install tensorflow_text
import tensorflow_text as text

import os

# Install Transformers library 
!pip install transformers

import seaborn as sns
import matplotlib.pyplot as plt

plt.style.use('dark_background')

"""## II. GET AND OVERVIEW THE RAW DATASET


"""

!git clone https://github.com/Franck-Dernoncourt/pubmed-rct.git
!ls pubmed-rct

"""* There are 5 class: BACKGROUND, OBJECTIVE, METHODS, RESULTS, CONCLUSIONS"""

# Check the files inside PubMed_200k_RCT_numbers_replaced_with_at_sign
!ls pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/

"""Comments:

The dataset contains 3 files, which are:
* dev.txt = validation set
* test.txt = test set
* train.zip = train set
"""

data_dir = '/content/pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/'

# Check all filenames inside the data_dir
filenames = [data_dir + filename for filename in os.listdir(data_dir)]
filenames

# Create a function to read a text filename and return the lines of text as a list
def get_lines(filename):
    with open(filename, 'r') as f:
        return f.readlines()

# Read the lines from dev, train, and test.txt to the appropriate lists (for 20k dataset)
train_list = get_lines('/content/pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/train.txt')
val_list = get_lines('/content/pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/dev.txt')
test_list = get_lines('/content/pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/test.txt')

train_list[:5]

val_list[:5]

test_list[:5]

"""Comments: the data is in list form
* Beginning: each abstract starts with "###numerical_id\n" format
* Ending: an empty new line "\n"
* Content: each line ob sentences includes: label + \t (tab seperated) + sentence
"""

len(train_list), len(val_list), len(test_list)

"""## III. PREPROCESS DATA & EDA"""

def preprocess_text_with_line_number(filename):
    input_lines = get_lines(filename) # get the list of all lines from filename
    abstract_lines = '' # create an empty abstract
    abstract_dataset = [] # create an empty list of abstracts

    for line in input_lines:
        if line.startswith('###'): # check whether the line is an ID line
            abstract_id = line
            abstract_lines = '' # reset the abstract string if the line is an ID line

        elif line.isspace(): # check whether the line is a new line "\n"
            abstract_line_split = abstract_lines.splitlines() # split abstract into a list of seperate line

            # Iterate through each line in a single abstract and count them at the same time
            for abstract_line_number, abstract_line in enumerate(abstract_line_split): # loop and create the tuple of each line number and the line content
                line_data = {} # create an empty dictionary for each line
                label_text_split = abstract_line.split('\t') # split label from text
                line_data['label'] = label_text_split[0] # get label
                line_data['text'] = label_text_split[1].lower() # get target text and lower so as to prevent bias between captialized and uncapitalized words
                line_data['line_number'] = abstract_line_number # the order that the line appears in the abstract
                line_data['total_lines'] = len(abstract_line_split) - 1 # total number of line in an abstract
                abstract_dataset.append(line_data) # add line data to abstract samples list

        else: # if the above conditions are not satisfiled, the line contains a labelled sentence
            abstract_lines += line

    return abstract_dataset

# Get data from file and preprocess
# All sets are lists of dictionaries
train_dict = preprocess_text_with_line_number('/content/pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/train.txt')
val_dict = preprocess_text_with_line_number('/content/pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/dev.txt')
test_dict = preprocess_text_with_line_number('/content/pubmed-rct/PubMed_20k_RCT_numbers_replaced_with_at_sign/test.txt')

len(train_dict), len(val_dict), len(test_dict)

# Check train dataset
train_dict[:1]

# Check validation dataset
val_dict[:1]

# Check test dataset
test_dict[:1]

import pandas as pd
# Converting list of dictionary data into DataFrame
train_df = pd.DataFrame(train_dict)
val_df = pd.DataFrame(val_dict)
test_df = pd.DataFrame(test_dict)

"""### 1. Training Dataset"""

# Overview the training dataset
train_df.head()

# 1. Train set information
print(f'{train_df.info()}\n')

# 2. Check null values
print(f'The training dataset has {train_df.isna().sum().sum()} null value(s).\n')

# 3. Check duplicated value
print(f'The training dataset has {train_df.duplicated().sum()} duplicated values.\n')

# 4. Check outliers

# Have a look at the duplicated lines
train_df[train_df.duplicated() == True]

"""Comments:

Theses above lines have

### 2. Validation Dataset
"""

# Overview the validation dataset
val_df.head()

# 1. Validation set information
print(f'{val_df.info()}\n')

# 2. Check null values
print(f'The validation dataset has {val_df.isna().sum().sum()} null value(s).\n')

# 3. Check duplicated value
print(f'The validation dataset has {val_df.duplicated().sum()} duplicated values.\n')

# 4. Check outliers

# Have a look at the duplicated lines
val_df[val_df.duplicated() == True]

"""### 3. Test Dataset"""

# Overview the test dataset
test_df.head()

# 1. Test set information
print(f'{test_df.info()}\n')

# 2. Check null values
print(f'The tets dataset has {test_df.isna().sum().sum()} null value(s).\n')

# 3. Check duplicated value
print(f'The test dataset has {test_df.duplicated().sum()} duplicated values.\n')

# 4. Check outliers

# Have a look at the duplicated lines
test_df[test_df.duplicated() == True]

# Distribution of labels in training data, validation data, and test data
print('Train set:')
print(train_df['label'].value_counts(), '\n')
print('Validation set:')
print(val_df['label'].value_counts(), '\n')
print('Test set:')
print(test_df['label'].value_counts())

# Check and compare the distribution of the abstract labels
import matplotlib.pyplot as plt
plt.style.use('dark_background')
plt.figure(figsize=(30,5))
plt.suptitle('DISTRIBUTION OF ABSTRACT LABELS')

plt.subplot(131)
train_df['label'].value_counts().plot(kind='barh')
plt.title('Train Dataset')
for index, value in enumerate(train_df['label'].value_counts()):
    plt.text(x=value+1000, y=index, s=value, fontsize='medium', ma='center')

plt.subplot(132)
val_df['label'].value_counts().plot(kind='barh')
plt.title('Validation Dataset')
for index, value in enumerate(val_df['label'].value_counts()):
    plt.text(x=value+100, y=index, s=value, fontsize='medium', ma='center')

plt.subplot(133)
test_df['label'].value_counts().plot(kind='barh')
plt.title('Test Dataset')
for index, value in enumerate(test_df['label'].value_counts()):
    plt.text(x=value+100, y=index, s=value, fontsize='medium', ma='center')

plt.show()

"""Comments:

* In all Training, Validation, and Test sets, there is an imbalance between **RESULTS**, **METHODS** and **CONCLUSIONS**, **BACKGROUND**, **OBJECTIVES**. However, it is considered to be acceptable because depending on the purpose of each section in the research papers, the many or fewer times they occur in the abstract are flexible.

* For instance, the paper is motivative targeted to answer only one question or solve the only big problem but multiple diverse methods and techniques are required to handle.

-> Therefore, we have to pay more attention to deal with this kind of inequality dataset.
"""

# Check the distribution of the length of the abstracts
plt.figure(figsize=(20,5))
plt.suptitle('NUMBER OF SENTENCES PER ABSTRACT')

plt.subplot(131)
sns.histplot(train_df['total_lines'], bins=25)
plt.title('Train Dataset')

plt.subplot(132)
sns.histplot(val_df['total_lines'], bins=25)
plt.title('Validation Dataset')

plt.subplot(133)
sns.histplot(test_df['total_lines'], bins=25)
plt.title('Test Dataset')

plt.show()

"""Comments:
* Most of the abstracts have the length between 7 to 17 sentences.
* On the other hand, the minority is from 2 to 6 and from 16 to 35 sentences.
* Validation and Test Dataset have the most similar sentence length distribution
"""

# Get lists of sentences only for all train, val, and test datasets
train_text_list = list(train_df['text'])
val_text_list = list(val_df['text'])
test_text_list = list(test_df['text'])

len(train_text_list), len(val_text_list), len(test_text_list)

train_text_list[:5]

val_text_list[:5]

test_text_list[:5]



# # Get the class of labels from LabelEncoder
# number_of_classes = len(label_encoder.classes_)
# name_of_label_class = label_encoder.classes_
# print('Number of classes:', number_of_classes, '\n', name_of_label_class)





# Create a list of sentence length
sentence_length = [len(sentence.split()) for sentence in train_text_list]

# Check the length of the longest sentence
print('The longest sentence has:', max(sentence_length), 'words.')

# Check the length of the shortest sentence
print('The shortest sentence has:', min(sentence_length), 'words.')

# Check the average spread of sentence length so as to find out the most general shape (length) for our data set
average_sentence_length = round(np.mean(sentence_length))
print('The average length of a sentence is:', average_sentence_length, 'words.')

# Check for the majority with quantile range is 95%
major_sentence_length = int(np.percentile(sentence_length, 95))
print('95% of the total sentences has:', major_sentence_length, 'words.')

# Visualize the distribution of sentence_length
import seaborn as sns
plt.figure(figsize=(10,5))
plt.title('DISTRIBUTION OF SENTENCE LENGTH')
sns.histplot(data=sentence_length, bins=25)

"""Comments:
* The vast majority of length per sentence is under 55 words (tokens).
* The average length of a sentence in an abstract is 26 words (tokens).
* The longest sentence has: 296 words.
* The shortest sentence has: 1 words ~ no empty sentences.
"""

print('Original training dataset:' , len(train_text_list), 'sentences')
print('95% of majority sentence length:', round(len(train_text_list)*0.95), 'sentences')
print('5% of minority sentence length:', round(len(train_text_list)*0.05), 'sentences')

"""Comments:

In general, 95% of the sentence length is under 54 words (tokens).

-> Therefore, 55 is chosen to be the maximum length threshold for text data vectorization output.

~ It would be an acceptable amount of 5% missing of the minor length (~ 9002 words).
"""

# Create a character-level tokenizer
# Create a function to split sentences into characters
def split_characters(text):
    text_split_list = ' '.join(list(text))
    return text_split_list

# Apply split_character function to train dataset
train_character_list = [split_characters(sentence) for sentence in train_text_list]
val_character_list = [split_characters(sentence) for sentence in val_text_list]
test_character_list = [split_characters(sentence) for sentence in test_text_list]

train_character_list[:5]

# Check the character length of each sentence
character_length = [len(sentence) for sentence in train_text_list]
average_character_length = np.mean(character_length)
average_character_length

# Check for the majority with quantile range is 95%
major_character_length = int(np.percentile(character_length, 95))
print('95% of the total sentences has:', major_character_length, 'characters')

# Visualize the distribution of character_length
import seaborn as sns
plt.figure(figsize=(10,5))
plt.title('DISTRIBUTION OF CHARACTER LENGTH')
sns.histplot(data=character_length, bins=25)

# Check the distribution of sequences at a character-level
import matplotlib.pyplot as plt
import seaborn as sns

sns.histplot(character_length, bins=15)





"""### Positional Embeddings
* Line numbers
* Total Lines
"""

# Check all available line numbers in the training dataset and their distribution
plt.figure(figsize=(20,5))
sns.countplot(train_df['line_number'])
plt.title(label='DISTRIBUTION OF SENTENCE ORDER IN ABSTRACT DATASET')
for index, value in enumerate(train_df['line_number'].value_counts()):
    plt.text(x=index, y=value+150, s=value, fontsize='medium', ha='center')

total_line_number = train_df['line_number'].count()
minor_line_number = train_df['line_number'][train_df['line_number'] > 15].count()
minor_line_percentage = round(minor_line_number/total_line_number*100, 2)
print(f'The total number of lines for minor line number is {minor_line_number} occupying nearly {minor_line_percentage} percent.')

"""Comments:

The lines number from 0 to 15 take the vast majority of the whole training dataset (~98%)

-> Dropping the minority lines number above 15 lines ~ 3101 lines (~1.72%) is acceptable.
"""

# Check all available total line numbers in the training dataset and their distribution
plt.figure(figsize=(20,5))
sns.countplot(train_df['total_lines'])
plt.title(label='DISTRIBUTION OF TOTAL LINES IN ABSTRACT DATASET')

train_df['total_lines'].describe()

number_of_total_lines = train_df['total_lines'].count()
minor_number_of_total_lines = train_df['total_lines'][train_df['total_lines'] > 20].count()
minor_number_of_total_lines_percentage = round(minor_number_of_total_lines/number_of_total_lines*100, 2)
print(f'The total number for total minor line number is {minor_number_of_total_lines} occupying nearly {minor_number_of_total_lines_percentage} percent.')

"""Comments:

The lines number from 0 to 20 take the vast majority of the whole training dataset (~98%)

-> Dropping the minority lines number above 20 total lines ~ 2373 lines (~1.32%) is acceptable.

#### SAVE DATASET FOR MODEL TRAINING
"""

# Save the dataframe as pickle file
train_df.to_pickle('/content/gdrive/MyDrive/abstract_section_classification/data/train_dataset.pkl')
val_df.to_pickle('/content/gdrive/MyDrive/abstract_section_classification/data/val_dataset.pkl')
test_df.to_pickle('/content/gdrive/MyDrive/abstract_section_classification/data/test_dataset.pkl')

"""### DISCOVER MORE:

1. Training, Validation, and Testing data preparation: https://colab.research.google.com/drive/1rN-BfkA5Vc5nMToka_Pyr1q1DtxlXxki#scrollTo=FhIyNphGtFAY

2. Model creation and training: https://colab.research.google.com/drive/1ZrEdJBmeU0FDtNN5F_s0eU6yqvAEIPMt#scrollTo=d0etEZ_Mpqw1&uniqifier=1

3. Demo data preprocessing and model prediction
https://colab.research.google.com/drive/1l3fQn91sOx7KbsLBiIPls_Aaw9CvAkFY#scrollTo=vS0raMb7tNqR
"""