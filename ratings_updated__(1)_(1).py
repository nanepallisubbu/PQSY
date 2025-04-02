# -*- coding: utf-8 -*-
"""Ratings_Updated__(1) (1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18Z-jdzO6ZVC4hfS17kP2NBhPwPDqF9Iu
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("muted")

column_names = ['user_id', 'product_id', 'Rating', 'timestamp']

try:
    df = pd.read_csv("/content/ratings.csv", names=column_names, header=None)
    print("Data loaded successfully!")
except FileNotFoundError:
    print("Error: ratings.csv not found!")
    raise

print(df.info())
print(df.head())

"""# Remove duplicates"""

initial_rows = len(df)
df.drop_duplicates(inplace=True)
print(f"Removed {initial_rows - len(df)} duplicate rows. New size: {len(df)}")

"""# Convert timestamp to datetime and add Days_Since_Start"""

df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
earliest_date = df['timestamp'].min()
df['Days_Since_Start'] = (df['timestamp'] - earliest_date).dt.days
df['Year'] = df['timestamp'].dt.year

"""# Verify no missing values"""

print("\nMissing Values:")
print(df.isnull().sum())

"""# Exploratory Data Analysis"""

print("\nRating Summary Statistics:")
print(df['Rating'].describe())

plt.figure(figsize=(10, 6))
sns.histplot(df['Rating'], bins=5, kde=True)
plt.title('Distribution of Ratings')
plt.xlabel('Rating')
plt.ylabel('Frequency')
plt.show()

"""# Average rating by year

"""

yearly_ratings = df.groupby('Year')['Rating'].mean()
plt.figure(figsize=(12, 6))
yearly_ratings.plot(kind='line', marker='o')
plt.title('Average Rating Over Time')
plt.xlabel('Year')
plt.ylabel('Average Rating')
plt.show()

"""# Ratings count by year

"""

yearly_counts = df['Year'].value_counts().sort_index()
plt.figure(figsize=(12, 6))
yearly_counts.plot(kind='bar')
plt.title('Number of Ratings by Year')
plt.xlabel('Year')
plt.ylabel('Count')
plt.show()

plt.figure(figsize=(14, 6))
sns.boxplot(x='Year', y='Rating', data=df)
plt.title('Rating Distribution by Year')
plt.xticks(rotation=45)
plt.show()

"""# Top users by rating count

"""

top_users = df['user_id'].value_counts().head(10)
print("\nTop 10 Users by Rating Count:")
print(top_users)

"""# Top products by rating count and average rating

"""

product_stats = df.groupby('product_id')['Rating'].agg(['count', 'mean']).sort_values('count', ascending=False).head(10)
print("\nTop 10 Products by Rating Count:")
print(product_stats)

"""# Scatter plot: Rating count vs. average rating for products

"""

plt.figure(figsize=(10, 6))
sns.scatterplot(data=product_stats, x='count', y='mean', size='count', hue='mean', palette='viridis')
plt.title('Product Popularity vs. Average Rating')
plt.xlabel('Number of Ratings')
plt.ylabel('Average Rating')
plt.show()

"""# Interactive scatter plot of ratings over time

"""

fig = px.scatter(df.sample(10000), x='Days_Since_Start', y='Rating', color='Rating',
                 title='Ratings Over Time (Sample of 10,000)',
                 labels={'Days_Since_Start': 'Days Since Earliest Rating', 'Rating': 'Rating'})
fig.update_layout(showlegend=False)
fig.show()

print("\nFinal Dataset Summary:")
print(f"Total Ratings: {len(df)}")
print(f"Unique Users: {df['user_id'].nunique()}")
print(f"Unique Products: {df['product_id'].nunique()}")
print(f"Time Span: {df['Year'].min()} to {df['Year'].max()}")

"""# Statistical Validation"""

from scipy import stats

print("\n--- Statistical Summary ---\n")
print(df.describe())

test_stat, p_value = stats.shapiro(df['Rating'])
print("\nShapiro-Wilk Test for Normality:", p_value)
if p_value > 0.05:
    print("Data appears normally distributed.")
else:
    print("Data is not normally distributed.")

plt.figure(figsize=(10,6))
numeric_df = df.select_dtypes(include=np.number)
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title("Feature Correlation Matrix")
plt.show()

ratings_by_year = [df[df['Year'] == year]['Rating'] for year in df['Year'].unique()]
valid_groups = [group for group in ratings_by_year if len(group) >= 2]

if len(valid_groups) < 2:
    print("\nANOVA Test for Rating Differences Across Years:")
    print("Error: Fewer than 2 years have sufficient data (2+ ratings). Cannot perform ANOVA.")
else:
    f_stat, p_value = stats.f_oneway(*valid_groups)
    print("\nANOVA Test for Rating Differences Across Years:")
    print(f"Years Analyzed: {len(valid_groups)} (filtered for 2+ ratings)")
    print(f"F-Statistic: {f_stat:.2f}")
    print(f"P-Value: {p_value:.4f}")
    if p_value < 0.05:
        print("Result: Significant differences in ratings across years (p < 0.05).")
    else:
        print("Result: No significant differences in ratings across years (p >= 0.05).")

sample_ratings = df['Rating'].sample(5000, random_state=42)
stat, p_value = stats.shapiro(sample_ratings)
print("\nShapiro-Wilk Test for Rating Normality:")
print(f"Statistic: {stat:.2f}")
print(f"P-Value: {p_value:.4f}")
if p_value < 0.05:
    print("Result: Ratings are not normally distributed (p < 0.05).")
else:
    print("Result: Ratings may be normally distributed (p >= 0.05).")

user_counts = df['user_id'].value_counts()
product_counts = df['product_id'].value_counts()
active_users = user_counts[user_counts >= 50].index
popular_products = product_counts[product_counts >= 100].index

df_subset = df[df['user_id'].isin(active_users) & df['product_id'].isin(popular_products)]
print(f"\nSubset Size: {len(df_subset)} rows")
print(f"Unique Users in Subset: {df_subset['user_id'].nunique()}")
print(f"Unique Products in Subset: {df_subset['product_id'].nunique()}")

from sklearn.model_selection import train_test_split

train_df, test_df = train_test_split(df_subset, test_size=0.2, random_state=42)
print(f"Training Set Size: {len(train_df)}")
print(f"Test Set Size: {len(test_df)}")

"""#Time Series"""

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

daily_ratings = df.groupby(df['timestamp'].dt.date)['Rating'].mean()

decomposition = seasonal_decompose(daily_ratings, model='additive', period=365)
decomposition.plot()
plt.show()

plt.figure(figsize=(12, 4))
plot_acf(daily_ratings, lags=50)
plt.title('Autocorrelation')
plt.show()

plt.figure(figsize=(12, 4))
plot_pacf(daily_ratings, lags=50)
plt.title('Partial Autocorrelation')
plt.show()

"""# Feature Preparation"""

from sklearn.preprocessing import LabelEncoder

X = df_subset.drop(['Rating', 'timestamp', 'Days_Since_Start', 'Year'], axis=1)
y = df_subset['Rating']

le_user = LabelEncoder()
le_product = LabelEncoder()

X['user_id'] = le_user.fit_transform(X['user_id'])
X['product_id'] = le_product.fit_transform(X['product_id'])

X_train = train_df.drop(['Rating', 'timestamp', 'Days_Since_Start', 'Year'], axis=1)
X_test = test_df.drop(['Rating', 'timestamp', 'Days_Since_Start', 'Year'], axis=1)
y_train = train_df['Rating']
y_test = test_df['Rating']

X_train['user_id'] = le_user.transform(X_train['user_id'])
X_train['product_id'] = le_product.transform(X_train['product_id'])
X_test['user_id'] = le_user.transform(X_test['user_id'])
X_test['product_id'] = le_product.transform(X_test['product_id'])

"""#Model Building and Evaluation"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

results = {}

models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'XGBoost': XGBClassifier(random_state=42),
    'Naive Bayes': GaussianNB(),
    'SVM': SVC(random_state=42)
}

if y_train.min() > 0:
    y_train_adjusted = y_train - y_train.min()
    y_test_adjusted = y_test - y_test.min()
else:
    y_train_adjusted = y_train
    y_test_adjusted = y_test

for name, model in models.items():
    print(f"\nTraining {name}...")
    if name == 'XGBoost':
        model.fit(X_train, y_train_adjusted)
        y_pred = model.predict(X_test)
        # Convert predictions back to original scale if needed
        if y_train.min() > 0:
            y_pred = y_pred + y_train.min()
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    #Evaluation code should be indented to be within the for

accuracy = accuracy_score(y_test, y_pred)
class_report = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

results[name] = {
        'accuracy': accuracy,
        'classification_report': class_report,
        'confusion_matrix': conf_matrix
    }

print(f"\n{name} Results:")
print(f"Accuracy: {accuracy:.4f}")
print("\nClassification Report:")
print(class_report)
print("\nConfusion Matrix:")
print(conf_matrix)

"""# Compare Results"""

best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
print("\nModel Comparison Summary:")
print("------------------------")
for name, metrics in results.items():
    print(f"{name}: Accuracy = {metrics['accuracy']:.4f}")

print(f"\nBest Model: {best_model[0]}")
print(f"Best Accuracy: {best_model[1]['accuracy']:.4f}")
print("\nBest Model Classification Report:")
print(best_model[1]['classification_report'])

plt.figure(figsize=(10, 6))
accuracies = [metrics['accuracy'] for metrics in results.values()]
model_names = list(results.keys())
sns.barplot(x=model_names, y=accuracies)
plt.title('Model Accuracy Comparison')
plt.ylabel('Accuracy')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

if 'Random Forest' in models:
    rf_model = models['Random Forest']
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    })
    feature_importance = feature_importance.sort_values('importance', ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='importance', y='feature', data=feature_importance)
    plt.title('Feature Importance (Random Forest)')
    plt.show()

