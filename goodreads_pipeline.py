import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json

# Set page config
st.set_page_config(
    page_title="Goodreads Data Pipeline",
    page_icon="📚",
    layout="wide"
)

class GoodreadsDataPipeline:
    def __init__(self):
        """Initialize the data pipeline."""
        self.raw_data = None
        self.processed_data = None
        self.user_interactions = None
        self.user_item_matrix = None
        self.drift_report = None
        
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    def load_data(self, file_path=None):
        """Load data from file or sample data."""
        if file_path:
            try:
                # Correct CSV loading with proper parameters
                self.raw_data = pd.read_csv(
                    file_path,
                    on_bad_lines='skip',  # Skip bad lines instead of erroring
                    encoding_errors='replace'  # Handle encoding issues
                )
                st.session_state['data_loaded'] = True
                return True
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
                return False
        else:
            st.warning("Using sample data for demonstration")
            sample_data = {
                'bookID': [1, 2, 3],
                'title': ['Sample Book 1', 'Sample Book 2', 'Sample Book 3'],
                'authors': ['Author A', 'Author B', 'Author C'],
                'average_rating': [4.1, 3.8, 4.5],
                'isbn': ['123', '456', '789'],
                'isbn13': ['1234567890123', '4567890123456', '7890123456789'],
                'language_code': ['eng', 'eng', 'spa'],
                'num_pages': [300, 250, 400],
                'ratings_count': [1000, 500, 1500],
                'text_reviews_count': [50, 30, 70],
                'publication_date': ['1/1/2020', '2/15/2019', '5/10/2021'],
                'publisher': ['Publisher X', 'Publisher Y', 'Publisher Z']
            }
            self.raw_data = pd.DataFrame(sample_data)
            st.session_state['data_loaded'] = True
            return True

    def clean_data(self):
        """Clean and preprocess the data."""
        if not hasattr(self, 'raw_data') or self.raw_data is None:
            st.error("No data loaded. Please load data first.")
            return False
        
        with st.spinner("Cleaning data..."):
            progress_bar = st.progress(0)
            self.processed_data = self.raw_data.copy()
            
            # Basic cleaning
            self.processed_data = self.processed_data.drop_duplicates(subset=['title', 'authors'])
            self.processed_data = self.processed_data.dropna(subset=['title', 'authors'])
            progress_bar.progress(20)
            
            # Standardize author names
            self.processed_data['authors'] = self.processed_data['authors'].str.split('/').str[0].str.strip()
            progress_bar.progress(30)
            
            # Clean publication date
            self.processed_data['publication_date'] = pd.to_datetime(
                self.processed_data['publication_date'], 
                errors='coerce',
                format='%m/%d/%Y'
            )
            self.processed_data['publication_year'] = self.processed_data['publication_date'].dt.year
            progress_bar.progress(50)
            
            # Clean language codes
            self.processed_data['language_code'] = self.processed_data['language_code'].str.lower().str.strip()
            progress_bar.progress(60)
            
            # Process genres (simplified example)
            self.processed_data['genres'] = self.processed_data['publisher'].apply(
                lambda x: [x.strip().lower()] if pd.notnull(x) else []
            )
            progress_bar.progress(80)
            
            # Select and rename columns
            self.processed_data = self.processed_data.rename(columns={
                'bookID': 'book_id',
                'average_rating': 'avg_rating',
                'ratings_count': 'num_ratings'
            })
            progress_bar.progress(100)
            
            st.session_state['data_cleaned'] = True
            return True

    # [Rest of the methods remain unchanged from previous implementation]

def main():
    st.title("📚 Goodreads Data Pipeline")
    st.markdown("""
    This pipeline processes Goodreads book data, generates user interactions, 
    creates recommendation matrices, and monitors for data drift.
    """)
    
    pipeline = GoodreadsDataPipeline()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    steps = [
        "Load Data",
        "Clean Data",
        "Generate Interactions",
        "Create Matrix",
        "Detect Drift",
        "Save Outputs"
    ]
    current_step = st.sidebar.radio("Go to", steps)
    
    # Step 1: Load Data
    if current_step == "Load Data":
        st.header("Step 1: Load Data")
        st.markdown("Upload your Goodreads data file or use sample data for demonstration.")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        col1, col2 = st.columns(2)
        with col1:
            if uploaded_file is not None:
                if st.button("Load Uploaded File"):
                    if pipeline.load_data(uploaded_file):
                        st.success("Data loaded successfully!")
                        st.dataframe(pipeline.raw_data.head())
        
        with col2:
            if st.button("Use Sample Data"):
                if pipeline.load_data():
                    st.success("Sample data loaded successfully!")
                    st.dataframe(pipeline.raw_data.head())
    
    # [Rest of the main function remains unchanged]

if __name__ == "__main__":
    main()