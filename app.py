import streamlit as st
from PIL import Image
import base64
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO

# Set up Streamlit page
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Load the AI Robot Image and convert it to base64
image_path = "image.png"
with open(image_path, "rb") as img_file:
    encoded_image = base64.b64encode(img_file.read()).decode()

# Custom CSS for perfect alignment
st.markdown("""
    <style>
        .title-container {
            display: inline-flex;
            align-items: center;
            gap: 2px;
        }
.title-container h1 {
    background: linear-gradient(to right, #00BFFF, #20B2AA); /* Sky Blue to Teal Gradient */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 50px;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    display: inline-block;
}

.large-letter {
    font-size: 65px; /* Larger size for D and S */
    font-weight: 900;
}

        .title-container img {
            vertical-align: middle;
        }
        .subtitle {
            font-size: 20px !important;
            font-weight: bold;
            margin-top: -10px;
        }
            .title-container h1 {
            color: #00BFFF !important;
        }
        .subtitle {
            color: grey !important;
        }
        h2, h3, h4, h5, h6 {
            color:teal !important;
        }
    </style>
""", unsafe_allow_html=True)

# Embed the image beside the title
st.markdown(f"""
<div class="title-container">
    <h1><span class="large-letter">D</span>ata <span class="large-letter">S</span>weeper</h1>
    <img src="data:image/png;base64,{encoded_image}" width="65">
</div>
""", unsafe_allow_html=True)

# Subtitle
st.markdown("<p class='subtitle'>🚀 Transform your files between CSV & Excel formats with built-in Data Cleaning & Visualization!</p>", unsafe_allow_html=True)

# File Uploading
uploaded_files = st.file_uploader("Upload your Excel/CSV files:", type=["csv", "xlsx"], accept_multiple_files=True)

# Store data in session state to persist changes
if "dataframes" not in st.session_state:
    st.session_state.dataframes = {}

if uploaded_files:
    # st.write("#### Uploaded Files")
    file_table = []
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        file_size_kb = file.getbuffer().nbytes / 1024
        
        # Read the file and store it in session state (if not already stored)
        if file.name not in st.session_state.dataframes:
            if file_ext == ".csv":
                st.session_state.dataframes[file.name] = pd.read_csv(file)
            elif file_ext == ".xlsx":
                st.session_state.dataframes[file.name] = pd.read_excel(file)
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue  # Skip unsupported file types
        
        file_table.append((file.name, file_ext, f"{file_size_kb:.2f} KB"))
    
    # Display uploaded files in a structured table
    st.write("### Uploaded Files")
    file_df = pd.DataFrame(file_table, columns=["File Name", "File Type", "File Size (KB)"])
    st.dataframe(file_df)
    
    # # Add file removal option within the table
    # for file_name, file_ext, file_size in file_table:
    #     col1, col2, col3 = st.columns([4, 2, 1])
    #     col1.write(file_name)
    #     col2.write(file_size)
    #     if col3.button("Remove", key=file_name):
    #         del st.session_state.dataframes[file_name]
    #         st.experimental_rerun()

    # Further Processing Section
    if st.session_state.dataframes:
        st.subheader("Further Processing for Data Cleaning & Visualization")

        # Let the user select a file for further processing
        file_names = list(st.session_state.dataframes.keys())
        selected_file = st.selectbox("Select a file for further processing", file_names)
        df = st.session_state.dataframes[selected_file]

        # Show Data Preview
        st.write(f"###### Preview of {selected_file}")
        st.dataframe(df.head())
        
        # Data Cleaning Options
        st.write("#### Data Cleaning Options")
        if st.checkbox(f"Clean data for {selected_file}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove Duplicates from {selected_file}"):
                    st.session_state.dataframes[selected_file] = df.drop_duplicates()
                    st.write("✅ Duplicates Removed!")
            with col2:
                if st.button(f"Fill Missing Values for {selected_file}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean().round(0).astype(int))
                    st.session_state.dataframes[selected_file] = df
                    st.write("✅ Missing values have been filled!")

        # Data Visualization
        st.write("#### Data Visualization Options")
        numeric_df = df.select_dtypes(include='number')
        if numeric_df.shape[1] >= 2:
            x_axis = st.selectbox("Select X-axis", [None] + list(numeric_df.columns), key="x_axis")
            y_axis = st.selectbox("Select Y-axis", [None] + list(numeric_df.columns), key="y_axis")

            if x_axis and y_axis:
                if x_axis == y_axis:
                    st.warning("X-axis and Y-axis cannot be the same! Please select different columns.")
                else:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        bar_chart = st.button("📊 Bar Chart")
                    with col2:
                        line_chart = st.button("📈 Line Chart")
                    with col3:
                        pie_chart = st.button("🥧 Pie Chart")

                    # Plotting based on selected chart
                    if bar_chart:
                        fig, ax = plt.subplots(figsize=(5, 2))
                        numeric_df.plot(kind="bar", x=x_axis, y=y_axis, ax=ax)
                        st.pyplot(fig)

                    elif line_chart:
                        fig, ax = plt.subplots(figsize=(5, 2))
                        numeric_df.plot(kind="line", x=x_axis, y=y_axis, ax=ax)
                        st.pyplot(fig)

                    elif pie_chart:
                        if numeric_df[x_axis].nunique() > 10:
                            st.warning("Too many unique values for a pie chart! Select a categorical column.")
                        else:
                            fig, ax = plt.subplots(figsize=(3, 3))
                            numeric_df.groupby(x_axis)[y_axis].sum().plot(kind="pie", autopct='%1.1f%%', ax=ax)
                            st.pyplot(fig)
            else:
                st.warning("Please select both X and Y axes to proceed with visualization.")



# File Conversion - Csv tpo excel or vice versa

    st.write("#### Conversion Options")
    conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

    if st.button(f"Convert {file.name}"):
        buffer = BytesIO()
        
        if conversion_type == "CSV":
            df.to_csv(buffer, index=False)
            file_name = file.name.replace(file_ext, ".csv")
            mime_type = "text/csv"
        
        elif conversion_type == "Excel":
            df.to_excel(buffer, index=False, engine='xlsxwriter')  # Corrected to use Excel format
            file_name = file.name.replace(file_ext, ".xlsx")
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        buffer.seek(0)

        # Download button
        st.download_button(
            label=f"Download {file.name} as {conversion_type}",
            data=buffer,
            file_name=file_name,
            mime=mime_type
        )

        st.success("✅ File conversion successful!")








# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 16px; color: darkgray;'>"
    "Powered by Streamlit | Designed for Governer Sindh IT Intiative Project by Asym Dabeer"
    "</p>", unsafe_allow_html=True
)
