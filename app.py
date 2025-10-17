import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
# Use st.set_page_config as the first Streamlit command
st.set_page_config(
    page_title="Bank Marketing Analytics Dashboard",
    layout="wide"
)

# --- CUSTOM CSS ---
# Inject custom CSS for a more polished and professional look
st.markdown("""
<style>
    /* General body styling */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Main header styling */
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        color: #0d3b66;
        text-align: center;
        margin-bottom: 0px;
        padding-top: 0px;
    }

    /* Sub-header for context */
    .sub-header {
        font-size: 1.2rem;
        color: #4f4f4f;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Style for metric cards */
    .metric-container {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: box-shadow 0.3s ease-in-out;
    }
    .metric-container:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Style for section headers */
    .section-header {
        font-size: 1.6rem;
        color: #0d3b66;
        border-bottom: 2px solid #eeeeee;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data(uploaded_file):
    """Reads and caches the uploaded CSV file."""
    if uploaded_file is not None:
        try:
            return pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return None
    return None

# --- MAIN APPLICATION ---
def main():
    # --- SIDEBAR: CONTROLS & FILE UPLOAD ---
    with st.sidebar:
        st.header("Controls & Setup")
        
        # Improvement: File uploader moved to the sidebar for better layout
        uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

    # --- MAIN PANEL ---
    
    # Display headers
    st.markdown('<p class="main-header">Bank Marketing Campaign Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">An interactive dashboard to explore customer demographics and campaign outcomes.</p>', unsafe_allow_html=True)

    # Logic to handle file upload
    if uploaded_file is None:
        st.info("Please upload a CSV file using the sidebar to begin analysis.")
        return

    df = load_data(uploaded_file)

    if df is None or df.empty:
        st.warning("The uploaded file is empty or could not be read. Please try another file.")
        return

    # --- SIDEBAR FILTERS (continued) ---
    # These filters appear only after data is loaded successfully
    with st.sidebar:
        st.header("Filters")
        
        # Dynamic filter for categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            selected_cat_col = st.selectbox('Select a categorical column for filtering:', categorical_cols)
            unique_vals = df[selected_cat_col].unique()
            selected_val = st.multiselect(f'Filter by {selected_cat_col}:', unique_vals, default=unique_vals)
            df = df[df[selected_cat_col].isin(selected_val)]

        # Dynamic filter for numerical columns (like age)
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
        if 'age' in numerical_cols:
            age_range = st.slider('Filter by Age Range', 
                                  min_value=int(df['age'].min()), 
                                  max_value=int(df['age'].max()), 
                                  value=(int(df['age'].min()), int(df['age'].max())))
            df = df[(df['age'] >= age_range[0]) & (df['age'] <= age_range[1])]

    # --- KEY METRICS ---
    st.markdown('<p class="section-header">Dashboard at a Glance</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    # Improvement: Using styled containers for metrics
    with col1:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Total Records", f"{len(df):,}")
            st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("Total Attributes", len(df.columns))
            st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        with st.container():
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            avg_age = df['age'].mean() if 'age' in df.columns else 'N/A'
            st.metric("Average Age", f"{avg_age:.1f}" if isinstance(avg_age, (int, float)) else avg_age)
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TABS FOR ORGANIZED CONTENT ---
    tab1, tab2, tab3 = st.tabs(["Data Overview", "Visual Analysis", "Export Data"])
    
    with tab1:
        st.markdown('<p class="section-header">Data Preview & Statistics</p>', unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown("---")
        st.subheader("Summary Statistics")
        st.dataframe(df.describe(include='all'), use_container_width=True)
    
    with tab2:
        st.markdown('<p class="section-header">Visual Data Exploration</p>', unsafe_allow_html=True)
        
        # Improvement: Let user select columns for plotting
        plot_col1, plot_col2 = st.columns(2)
        with plot_col1:
            x_axis = st.selectbox("Select X-axis for plots", options=df.columns, index=0)
        with plot_col2:
            y_axis_options = [None] + df.columns.tolist()
            y_axis = st.selectbox("Select Y-axis for plots (optional)", options=y_axis_options, index=0)

        # Improvement: Use Plotly for interactive and professional charts
        plot_col_1, plot_col_2 = st.columns(2)
        with plot_col_1:
             st.subheader("Distribution (Histogram)")
             try:
                fig1 = px.histogram(df, x=x_axis, title=f'Distribution of {x_axis}', color_discrete_sequence=['#0d3b66'])
                st.plotly_chart(fig1, use_container_width=True)
             except Exception as e:
                st.warning(f"Could not create histogram: {e}")

        with plot_col_2:
            st.subheader("Relationship Plot")
            if y_axis:
                try:
                    fig2 = px.scatter(df, x=x_axis, y=y_axis, title=f'{x_axis} vs. {y_axis}', color=x_axis)
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not create scatter plot: {e}")
            else:
                st.info("Select a Y-axis to view a relationship plot.")
    
    with tab3:
        st.markdown('<p class="section-header">Export Processed Data</p>', unsafe_allow_html=True)
        st.write("Click below to download the currently filtered dataset as a CSV file.")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name="filtered_bank_data.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
