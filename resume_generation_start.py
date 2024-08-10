# -*- coding: utf-8 -*-
"""Resume Generation Start.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1o5CikO-pCXPzDR-DU4gKnhi--INKEQ0C

### This is the first project that i did for resume generation. I read the topic wrong and did it a little wrong, but this is a better project and has a very large dataset to work witgh as well
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from wordcloud import WordCloud

import matplotlib.pyplot as plt
# %matplotlib inline
from textblob import Word
# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

test = pd.read_csv('/content/drive/MyDrive/AAI/train.csv')
test = test.dropna()
print("\n ** raw data **\n")
print(test.head())
print("\n ** data shape **\n")
print(test.shape)

fig = plt.figure(figsize=(300, 10), dpi=200, facecolor='w', edgecolor='k')
test.Job_Title.hist(bins=len(test.Job_Title.unique()))  # Set number of bins to the number of unique job titles
plt.show()
print(len(test.Job_Title.unique()))

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

import nltk
nltk.download('wordnet')

from nltk.corpus import wordnet

## Lower case
test['skills'] = test['skills'].apply(lambda x: " ".join(x.lower()for x in x.split()))
## remove tabulation and punctuation
test['skills'] = test['skills'].str.replace('[^\w\s]',' ')
## digits
test['skills'] = test['skills'].str.replace('\d+', '')

#remove stop words
stop = stopwords.words('english')
test['skills'] = test['skills'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))

## lemmatization
test['skills'] = test['skills'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))

print("Preprocessed data: \n")
print(test.head())

## jda stands for job description aggregated
jda = test.groupby(['Job_Title']).sum().reset_index()
print("Aggregated job descriptions: \n")
print(jda)

## Visualize data
jobs_list = jda.Job_Title.unique().tolist()
for job in jobs_list:

    # Start with one review:
    text = jda[jda.Job_Title == job].iloc[0].skills
    # Create and generate a word cloud image:
    wordcloud = WordCloud().generate(text)
    print("\n***",job,"***\n")
    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

## Delete more stop words
other_stop_words = ['junior', 'senior','experience','etc','job','work','company','technique',
                    'candidate','skill','skills','language','menu','inc','new','plus','years',
                   'technology','organization','ceo','cto','account','manager','data','scientist','mobile',
                    'developer','product','revenue','strong','ass']

test['skills'] = test['skills'].apply(lambda x: " ".join(x for x in x.split() if x not in other_stop_words))

## Converting text to features
vectorizer = TfidfVectorizer()
#Tokenize and build vocabulary
X = vectorizer.fit_transform(test.skills)
y = test.Job_Title

# split data into 80% training and 20% test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state=109)
print("train data shape: ",X_train.shape)
print("test data shape: ",X_test.shape)

# Fit model
clf = MultinomialNB()
clf.fit(X_train, y_train)
## Predict
y_predicted = clf.predict(X_test)

fig = plt.figure(figsize=(300, 10), dpi=200, facecolor='w', edgecolor='k')

y_train.hist()
y_test.hist()

#evaluate the predictions
print("Accuracy score is: ",accuracy_score(y_test, y_predicted))
print("Classes: (to help read Confusion Matrix)\n", clf.classes_)
print("Confusion Matrix: ")

print(confusion_matrix(y_test, y_predicted))
print("Classification Report: ")
print(classification_report(y_test, y_predicted))

"""Our accuracy score is 64% which is acceptable.

NOTE: Model accuracy dropped down after deleting the job titles from their respective descriptions. Which is expectable. ( If most job descriptions for CEO contain the word CEO, then the token CEO will be the most important feature for the class CEO)

This way our model will give more weight to other remaining/meaningful tokens

The confusion matrix shows that the features for the account manager, data scientist and mobile developer are differenciable. Therefore, we expect to extract meaningful features out of these classes.
"""

import nltk
nltk.download('punkt')

import nltk
nltk.download('averaged_perceptron_tagger')

from textblob import TextBlob
import pandas as pd

technical_skills = ['python', 'c', 'r', 'c++', 'java', 'hadoop', 'scala', 'flask', 'pandas', 'spark', 'scikit-learn',
                    'numpy', 'php', 'sql', 'mysql', 'css', 'mongdb', 'nltk', 'fastai', 'keras', 'pytorch', 'tensorflow',
                    'linux', 'Ruby', 'javascript', 'django', 'react', 'reactjs', 'ai', 'ui', 'tableau','angular']

feature_array = vectorizer.get_feature_names_out()

# Number of overall model features
features_numbers = len(feature_array)
## Max sorted features number
n_max = int(features_numbers * 0.1)

## Initialize output dataframe
output_data = []

for i in range(0, len(clf.classes_)):
    print("\n****", clf.classes_[i], "****\n")
    class_prob_indices_sorted = clf.feature_log_prob_[i, :].argsort()[::-1]
    raw_skills = np.take(feature_array, class_prob_indices_sorted[:n_max])
    print("List of unprocessed skills:")
    print(raw_skills)

    ## Extract technical skills
    top_technical_skills = list(set(technical_skills).intersection(raw_skills))[:6]

    # Transform list to string
    txt = " ".join(raw_skills)
    blob = TextBlob(txt)
    # Top 6 adjectives
    top_adjectives = [w for (w, pos) in TextBlob(txt).pos_tags if pos.startswith("JJ")][:6]

    # Append data to the list of dictionaries
    output_data.append({'Job_Title': clf.classes_[i],
                        'technical_skills': top_technical_skills,
                        'soft_skills': top_adjectives})

# Create a DataFrame from the list of dictionaries
output = pd.DataFrame(output_data)

# Display the resulting DataFrame
print(output)

print(output.T)

import pandas as pd

# Load the job dataset
csv_data = pd.read_csv('/content/drive/MyDrive/AAI/train.csv')

# Function to recommend job titles based on user's skills
def recommend_job_titles(skills):
    # Extract unique job titles
    job_titles = csv_data["Job_Title"].unique()

    # Find job titles with matching skills in the job description
    matched_titles = []
    for title in job_titles:
        # Get job description for the current title
        job_description = csv_data[csv_data["Job_Title"] == title]["skills"].iloc[0]
        # Check if any of the user's skills match with the job description
        if any(skill.lower() in job_description.lower() for skill in skills):
            matched_titles.append(title)

    return matched_titles

# Function to generate a sample resume based on the selected job title
def generate_resume(job_title, skills):
    resume = {
        "Personal Information": {
        "Name": "ABC XYZ",
        "Contact Information": {
        "Email": "abs.xyz@example.com",
        "Phone": "123-456-7890",
        "LinkedIn": "linkedin.com/in/abc_xyz",
            },
        },
        "Skills": skills,
        "Job Title": job_title,
        "Job Description": None,
        "Responsibilities": None,
        "Benefits": None,
        "Company Profile": None,
    }

    # Fetch job-related details from the dataset
    job_data = csv_data[csv_data["Job_Title"] == job_title]
    if not job_data.empty:
        resume["Job Description"] = job_data["Job_Description"].iloc[0]
        resume["Responsibilities"] = job_data["Responsibilities"].iloc[0]
        resume["Benefits"] = job_data["Benefits"].iloc[0]
        resume["Company Profile"] = job_data["Company Profile"].iloc[0]

    return resume


# User input for skills
user_skills = ["css"]  # Example input of skills the user is good at

# Recommend job titles based on the user's skills
recommended_titles = recommend_job_titles(user_skills)

# Display recommended job titles and allow user to choose one
print("Recommended job titles:")
for idx, title in enumerate(recommended_titles):
    print(f"{idx + 1}. {title}")

# User selects one of the recommended job titles
selected_idx = int(input())  # Example: User chooses the first recommended title
selected_job_title = recommended_titles[selected_idx - 1]  # Convert index to title

# Generate a resume for the selected job title
sample_resume = generate_resume(selected_job_title, user_skills)

# Display the generated sample resume
print("\nSample Resume:")
for key, value in sample_resume.items():
    if isinstance(value, dict):
        print(f"{key}:")
        for sub_key, sub_value in value.items():
            print(f"  {sub_key}: {sub_value}")
    else:
        print(f"{key}: {value}")

import pandas as pd

word = 'css'

# Count how many rows contain the specific word
rows_with_word = test['skills'].str.contains(word, case=False).sum()

print(f"The word '{word}' appears in {rows_with_word} rows.")

import pandas as pd
from collections import Counter

# Load the dataset
df = pd.read_csv('/content/drive/MyDrive/AAI/train.csv')  # Change this to the path where your CSV file is located

# Simplified text processing: convert to lowercase, remove punctuation and digits
df['skills'] = df['skills'].str.lower()
df['skills'] = df['skills'].str.replace('[^\w\s]', ' ', regex=True)
df['skills'] = df['skills'].str.replace('\d+', '', regex=True)

# Function to extract keywords (the most frequent words) from skills
def extract_keywords(text):
    words = text.split()  # Just split the text into words without removing stopwords
    word_freq = Counter(words)
    # Get the 10 most common words as a simple 'word cloud'
    return ', '.join([word for word, freq in word_freq.most_common(10)])

# Apply keyword extraction to each job title group and get the top keywords
df['word_cloud'] = df['skills'].apply(extract_keywords)

# Save the DataFrame to a CSV file
df[['Job_Title', 'word_cloud']].to_csv('submission.csv', index=False)

print("The CSV file has been created with the job titles and the corresponding 'word clouds'.")

import pandas as pd
from collections import Counter
from IPython.display import FileLink

# Load the dataset
df = pd.read_csv('/content/drive/MyDrive/AAI/train.csv')  # Adjust this to your CSV file's location

# Simplified text processing: convert to lowercase, remove punctuation and digits
df['skills'] = df['skills'].str.lower()
df['skills'] = df['skills'].str.replace('[^\w\s]', ' ', regex=True)
df['skills'] = df['skills'].str.replace('\d+', '', regex=True)

# Function to extract keywords (the most frequent words) from skills
def extract_keywords(text):
    words = text.split()  # Just split the text into words without removing stopwords
    word_freq = Counter(words)
    # Get the 10 most common words as a simple 'word cloud'
    return ', '.join([word for word, freq in word_freq.most_common(10)])

# Apply keyword extraction to each job title group and get the top keywords
df['word_cloud'] = df['skills'].apply(extract_keywords)

# Save the DataFrame to a CSV file
output_file = 'submission.csv'
df[['Job_Title', 'word_cloud']].to_csv(output_file, index=False)

# Display the DataFrame in the notebook
display(df[['Job_Title', 'word_cloud']])

import pandas as pd
from collections import Counter

# Load the dataset
df = pd.read_csv('/content/drive/MyDrive/AAI/train.csv')  # Adjust this to your CSV file's location

# Simplified text processing: convert to lowercase, remove punctuation and digits
df['skills'] = df['skills'].str.lower()
df['skills'] = df['skills'].str.replace('[^\w\s]', ' ', regex=True)
df['skills'] = df['skills'].str.replace('\d+', '', regex=True)

# Function to extract keywords (the most frequent words) from skills
def extract_keywords(text):
    words = text.split()  # Just split the text into words without removing stopwords
    word_freq = Counter(words)
    # Get the 10 most common words as a simple 'word cloud'
    return ', '.join([word for word, freq in word_freq.most_common(10)])

# Apply keyword extraction to each job title group and get the top keywords
df['skills'] = df['skills'].apply(extract_keywords)

# Add an 'id' column starting from 0
df.reset_index(drop=True, inplace=True)
df.index.name = 'id'

# Select only the 'id' and 'skills' columns and save to a CSV file
output_file = 'submission.csv'
df[['skills']].to_csv(output_file, index=True, index_label='id')

# Print the final DataFrame structure (optional)
print(df[['skills']])