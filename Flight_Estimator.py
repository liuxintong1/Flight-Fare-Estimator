import streamlit as st
from Mini_DataFrame import MyTable


def load_flight_data():
    csv_path = "US Airline Flight Routes and Fares 1993-2024.csv"
    try:
        return MyTable.from_file(csv_path)
    except FileNotFoundError:
        st.error("Error: CSV file not found.")
        return None


def main():
    st.set_page_config(page_title="Flight Estimator", layout="wide")
    st.title("Flight Fare Estimator")
    
    flights = load_flight_data()
    if flights is None:
        return
    
    # Project (select) only the required columns
    required_columns = [
        "Year",
        "quarter",
        "citymarketid_1",
        "citymarketid_2",
        "city1",
        "city2",
        "airportid_1",
        "airportid_2",
        "airport_1",
        "airport_2",
        "nsmiles",
        "fare",
        "fare_low"
    ]
    
    # Project to keep only the required columns that exist
    flights = flights.select(required_columns)
    
    # Find city and airport columns
    city1_col = "city1"
    city2_col = "city2"
    airport1_col = "airport_1"
    airport2_col = "airport_2"
    
    # Remove empty cities
    flights = flights.drop_missing(columns=[city1_col, city2_col, airport1_col, airport2_col])
    
    # Code Examples Section
    st.divider()
    
    with st.expander("📝 Code Examples: MyTable Functions", expanded=False):
        st.subheader("📝 Code Examples: MyTable Functions")
        
        code_tab1, code_tab2, code_tab3, code_tab4 = st.tabs(["Data Loading", "Data Processing", "GroupBy & Aggregation", "Join Operations"])
        
        with code_tab1:
            st.write("**MyTable.from_file()** - Class method to load CSV data")
            st.code("""
def load_flight_data():
    csv_path = "US Airline Flight Routes and Fares 1993-2024.csv"
    try:
        return MyTable.from_file(csv_path)
    except FileNotFoundError:
        st.error("Error: CSV file not found.")
        return None

flights = load_flight_data()
            """, language="python")
        
        with code_tab2:
            st.write("**select()** - Selects specific columns from the table")
            st.code("""
# Project to keep only the required columns that exist
required_columns = [
    "Year", "quarter", "city1", "city2", 
    "airport_1", "airport_2", "nsmiles", "fare", "fare_low"
]
flights = flights.select(required_columns)
            """, language="python")
            
            st.write("**drop_missing()** - Removes rows with missing values in specified columns")
            st.code("""
# Remove empty cities
city1_col = "city1"
city2_col = "city2"
airport1_col = "airport_1"
airport2_col = "airport_2"
flights = flights.drop_missing(columns=[city1_col, city2_col, airport1_col, airport2_col])
            """, language="python")
            
            st.write("**filter()** - Filters rows based on a condition function")
            st.code("""
# Filter by origin city
selected_origin_city = "New York"
filtered_flights = flights.filter(lambda row: row[city1_col] == selected_origin_city)

# Filter by destination city
selected_dest_city = "Los Angeles"
filtered_flights = filtered_flights.filter(lambda row: row[city2_col] == selected_dest_city)
            """, language="python")
        
        with code_tab3:
            st.write("**groupby()** - Groups rows by one or more columns and returns a GroupBy object")
            st.code("""
# Group by Year and quarter
grouped_by_year_quarter = filtered_flights.groupby(['Year', 'quarter'])
            """, language="python")
            
            st.write("**agg()** - Performs aggregation operations on grouped data")
            st.code("""
# Calculate average fare using agg()
# Available aggregation functions: 'mean', 'sum', 'count', 'min', 'max', 'median'
avg_fare_table = grouped_by_year_quarter.agg({'fare': 'mean'})

# The result contains columns: Year, quarter, fare_mean
# Access the aggregated results
for row in avg_fare_table.rows:
    year = row.get('Year')
    quarter = row.get('quarter')
    average_fare = row.get('fare_mean')
            """, language="python")
            
            st.write("**Example: Multiple aggregations**")
            st.code("""
# You can aggregate multiple columns at once
grouped = flights.groupby(['Year', 'quarter'])
result = grouped.agg({
    'fare': 'mean',      # Average fare
    'nsmiles': 'sum'     # Total miles
})
# Result columns: Year, quarter, fare_mean, nsmiles_sum
            """, language="python")
        
        with code_tab4:
            st.write("**join()** - Joins two MyTable objects on specified column(s)")
            st.code("""
# Example: Creating indirect flights by joining origin and destination tables
# Step 1: Filter and prepare tables
table_origin = flights.filter(lambda row: row[city1_col] == selected_origin_city)
table_destination = flights.filter(lambda row: row[city2_col] == selected_dest_city)

# Step 2: Create join key (composite key: connecting_city + Year + quarter)
# Add join_key to origin table - create new rows with join_key
origin_with_key_rows = []
for row in table_origin.rows:
    new_row = row.copy()
    new_row['join_key'] = f"{row['city2']}_{row['Year']}_{row['quarter']}"
    origin_with_key_rows.append(new_row)
table_origin_with_key = MyTable(table_origin.columns + ['join_key'], origin_with_key_rows)

# Add join_key to destination table - create new rows with join_key
dest_with_key_rows = []
for row in table_destination.rows:
    new_row = row.copy()
    new_row['join_key'] = f"{row['city1']}_{row['Year']}_{row['quarter']}"
    dest_with_key_rows.append(new_row)
table_destination_with_key = MyTable(table_destination.columns + ['join_key'], dest_with_key_rows)

# Step 3: Perform inner join
indirect_flights = table_origin_with_key.join(table_destination_with_key, on='join_key', how='inner')
            """, language="python")
    
    st.divider()
    
    # Get unique origin cities
    origin_cities = sorted(list(set([row[city1_col] for row in flights.rows])))

    origin_options = [""] + origin_cities

    # Initialize default origin only once
    if "origin_city" not in st.session_state:
        st.session_state.origin_city = (
            "Chicago, IL" if "Chicago, IL" in origin_options else ""
        )
   
    # Origin City Section
    selected_origin_city = st.selectbox(
        "🛫 Origin City:",
        origin_options,
        key="origin_city"
    )

    # Get unique destination cities
    dest_cities = sorted(list(set([row[city2_col] for row in flights.rows])))
    dest_options = [""] + dest_cities

    # Initialize default destination only once
    if "dest_city" not in st.session_state:
        st.session_state.dest_city = (
            "Los Angeles, CA (Metropolitan Area)" if "Los Angeles, CA (Metropolitan Area)" in dest_options else ""
        )
    # Destination City Section
    selected_dest_city = st.selectbox(
        "🛬 Destination City:",
        dest_options,
        key="dest_city"
    )
    
    # Interactive FAQ Section
    if selected_origin_city and selected_dest_city:
        st.divider()
        st.subheader("❓ Frequently Asked Questions")
        
        # Month to quarter mapping
        month_to_quarter = {
            'January': 1, 'February': 1, 'March': 1,
            'April': 2, 'May': 2, 'June': 2,
            'July': 3, 'August': 3, 'September': 3,
            'October': 4, 'November': 4, 'December': 4
        }
        
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
        
        # Display FAQ question with inline month selection
        # Use columns to keep everything on the same line
        col1, col2, col3 = st.columns([0.9, 1.5, 6.0])

        month_key = f"faq_month_{selected_origin_city}_{selected_dest_city}"

        with col1:
            st.markdown(
                "<p style='margin-bottom:0; padding-top:6px;'><strong>Q:</strong> I'm traveling in</p>",
                unsafe_allow_html=True
            )

        with col2:
            selected_month = st.selectbox(
                "",
                months,
                key=month_key,
                label_visibility="collapsed"
            )

        with col3:
            st.markdown(
                f"<p style='margin-bottom:0; padding-top:6px;'>"
                f", how much would a flight cost from "
                f"<strong>{selected_origin_city}</strong> to "
                f"<strong>{selected_dest_city}</strong> in 2025 and 2026?"
                f"</p>",
                unsafe_allow_html=True
            )
        
        # Initialize session state for projection data if not exists
        if 'direct_projection_data' not in st.session_state:
            st.session_state.direct_projection_data = None
        if 'indirect_projection_data' not in st.session_state:
            st.session_state.indirect_projection_data = None
        
        # Check if direct flights exist for the selected route (used by both FAQs)
        direct_flights_exist = False
        if selected_origin_city and selected_dest_city:
            temp_filtered = flights.filter(lambda row: row[city1_col] == selected_origin_city)
            temp_filtered = temp_filtered.filter(lambda row: row[city2_col] == selected_dest_city)
            direct_flights_exist = len(temp_filtered.rows) > 0
        
        # Check if indirect flights exist for the selected route (used by both FAQs)
        indirect_flights_exist = False
        if selected_origin_city and selected_dest_city:
            table_origin_check = flights.filter(lambda row: row[city1_col] == selected_origin_city)
            table_destination_check = flights.filter(lambda row: row[city2_col] == selected_dest_city)
            # Check if there's a potential connecting city (city2 from origin matches city1 from destination)
            if table_origin_check.rows and table_destination_check.rows:
                origin_cities_leg1 = set([row[city2_col] for row in table_origin_check.rows])
                dest_cities_leg2 = set([row[city1_col] for row in table_destination_check.rows])
                # If there's an overlap, indirect flights might exist
                if origin_cities_leg1.intersection(dest_cities_leg2):
                    indirect_flights_exist = True
        
        # Current route identifier
        current_route = f"{selected_origin_city}_{selected_dest_city}" if (selected_origin_city and selected_dest_city) else None
        
        # First FAQ: Travel cost for selected month
        # Only proceed if a month is selected
        if selected_month:
            # Determine which projection data to use
            # Check for direct first, then indirect (even if indirect_flights_exist check failed)
            if direct_flights_exist and st.session_state.direct_projection_data:
                projection_data = st.session_state.direct_projection_data
            elif st.session_state.indirect_projection_data:
                # Use indirect projections if available (regardless of indirect_flights_exist check)
                projection_data = st.session_state.indirect_projection_data
            else:
                projection_data = None
            
            if projection_data:
                selected_quarter = month_to_quarter[selected_month]
                # Find projections for the selected quarter and years 2025, 2026
                quarter_projections = [row for row in projection_data 
                                     if row.get('quarter') == selected_quarter and row.get('Year') in [2025, 2026]]
                
                if quarter_projections:
                    # Format the answer
                    fare_list = []
                    for proj in sorted(quarter_projections, key=lambda x: x.get('Year')):
                        year = proj.get('Year')
                        fare = proj.get('projected_fare', 'N/A')
                        # Ensure fare is a number and format it properly
                        if isinstance(fare, (int, float)):
                            fare_str = f"\\${fare:.2f}"  # Escape dollar sign for markdown
                        else:
                            fare_str = f"\\${fare}"
                        fare_list.append(f"{fare_str} in {year}")
                    
                    if len(fare_list) == 2:
                        answer_text = f"**A:** Usually the flight fare is {fare_list[0]} and {fare_list[1]}."
                    elif len(fare_list) == 1:
                        answer_text = f"**A:** Usually the flight fare is {fare_list[0]}."
                    else:
                        answer_text = f"**A:** Usually the flight fare is {', '.join(fare_list)}."
                    
                    st.markdown(answer_text)
                else:
                    st.write("**A:** Projection data not available for " + selected_month + " (Q" + str(selected_quarter) + ") in 2025-2026.")
            else:
                st.write("**A:** This information is not available.")
        
        # Second FAQ: Best time to travel
        st.markdown("---")
        st.markdown(f"**Q:** When is the best time to take a flight from {selected_origin_city} to {selected_dest_city}?")
        
        # Determine which projection data to use (priority: direct, then indirect)
        projection_data = None
        if direct_flights_exist and st.session_state.direct_projection_data:
            projection_data = st.session_state.direct_projection_data
        elif st.session_state.indirect_projection_data:
            # Use indirect projections if available (regardless of indirect_flights_exist check)
            projection_data = st.session_state.indirect_projection_data
        
        if projection_data:
            # Find all 2026 projections
            projections_2026 = [row for row in projection_data if row.get('Year') == 2026]
            
            if projections_2026:
                # Sort by quarter first to ensure consistent ordering
                projections_2026_sorted = sorted(projections_2026, key=lambda x: x.get('quarter', 0))
                
                # Find the quarter with the lowest fare
                # If there's a tie, pick the first one in quarter order (Q1, Q2, Q3, Q4)
                min_fare = float('inf')
                best_quarter = None
                for proj in projections_2026_sorted:
                    fare = proj.get('projected_fare')
                    if fare is not None and isinstance(fare, (int, float)):
                        if fare < min_fare:
                            min_fare = fare
                            best_quarter = proj.get('quarter')
                
                if best_quarter:
                    # Map quarter to months
                    quarter_to_months = {
                        1: ['January', 'February', 'March'],
                        2: ['April', 'May', 'June'],
                        3: ['July', 'August', 'September'],
                        4: ['October', 'November', 'December']
                    }
                    best_months = quarter_to_months.get(best_quarter, [])
                    months_str = ', '.join(best_months)
                    st.markdown(f"**A:** The best time to travel is {months_str}.")
                else:
                    st.write("**A:** This information is not available.")
            else:
                st.write("**A:** This information is not available.")
        else:
            st.write("**A:** This information is not available.")


        # Third FAQ: Should I wait or purchase now?
        st.markdown("---")
        
        # Get user input for current price
        col_price0, col_price1, col_price2 = st.columns([7, 1, 6.0])
        with col_price0:
            st.markdown(
                f"<p style='margin-bottom:0; padding-top:6px;'><strong>Q:</strong>"
                f"The current price for a flight from "
                f"<strong>{selected_origin_city}</strong> to "
                f"<strong>{selected_dest_city}</strong> is"
                f"</p>",
                unsafe_allow_html=True
            )
        with col_price1:
            current_price_input = st.number_input("", min_value=0.0, value=0.0, step=1.0, 
                                                 label_visibility="collapsed", 
                                                 key=f"current_price_{selected_origin_city}_{selected_dest_city}")
        with col_price2:
            st.markdown(
                f"<p style='margin-bottom:0; padding-top:6px;'>"
                f". Should I wait or purchase right now?</p>",
                unsafe_allow_html=True)
        
        # Get the 2026 projection from Q1 (based on selected month/quarter)
        if selected_month and current_price_input > 0:
            selected_quarter = month_to_quarter[selected_month]
            
            # Get projection data (same logic as Q1 - no route checking)
            projection_data_q3 = None
            if direct_flights_exist and st.session_state.direct_projection_data:
                projection_data_q3 = st.session_state.direct_projection_data
            elif st.session_state.indirect_projection_data:
                # Use indirect projections if available
                projection_data_q3 = st.session_state.indirect_projection_data
            
            if projection_data_q3:
                # Find 2026 projection for the selected quarter
                projection_2026 = None
                for row in projection_data_q3:
                    if row.get('Year') == 2026 and row.get('quarter') == selected_quarter:
                        projection_2026 = row.get('projected_fare')
                        break
                
                if projection_2026 and isinstance(projection_2026, (int, float)) and projection_2026 > 0:
                    # Calculate 30% of 2026 projection
                    thirty_percent = projection_2026 - projection_2026 * 0.3
                    
                    # Compare and provide recommendation
                    if current_price_input < thirty_percent:
                        st.markdown(f"**A:** Strong recommend to purchase now. The current price (\\${current_price_input:.2f}) is significantly lower, less than 70% of the projected 2026 fare (\\${projection_2026:.2f}).")
                    elif current_price_input > projection_2026:
                        st.markdown(f"**A:** I suggest waiting. The current price (\\${current_price_input:.2f}) is higher than the projected 2026 fare (\\${projection_2026:.2f}).")
                    else:
                        st.markdown(f"**A:** The current price (\\${current_price_input:.2f}) is normally priced compared to the projected 2026 fare (\\${projection_2026:.2f}). I recommend purchasing.")
                else:
                    st.write("**A:** Projection data not available for the selected month in 2026.")
            else:
                st.write("**A:** This information is not available.")
        elif current_price_input > 0:
            st.write("**A:** Please select a month in the first question to get a recommendation.")
        else:
            st.write("**A:** Please enter the current price to get a recommendation.")
    
    # Filter and display results
    st.divider()
    st.subheader("📊 Direct Flights")
    
    # Start with all flights
    filtered_flights = flights
    
    # Filter by origin city if selected
    if selected_origin_city:
        filtered_flights = filtered_flights.filter(lambda row: row[city1_col] == selected_origin_city)
    
    # Filter by destination city if selected
    if selected_dest_city:
        filtered_flights = filtered_flights.filter(lambda row: row[city2_col] == selected_dest_city)
    
    # Display direct flights in tabs
    if filtered_flights.rows:
        # Create tabs for the three views
        tab1, tab2, tab3 = st.tabs(["Direct Flights", "Average Fare by Year/Quarter", "Projections 2025-2026"])
        
        with tab1:
            st.write(f"**Found {len(filtered_flights.rows)} direct route record(s)**")
            st.dataframe(filtered_flights.rows, use_container_width=True)
        
        with tab2:
            # Calculate average fare by Year and quarter using agg()
            grouped_by_year_quarter = filtered_flights.groupby(['Year', 'quarter'])
            avg_fare_table = grouped_by_year_quarter.agg({'fare': 'mean'})
            
            # Convert agg results to the format we need
            avg_fare_results = []
            for row in avg_fare_table.rows:
                avg_fare_results.append({
                    'Year': row.get('Year'),
                    'quarter': row.get('quarter'),
                    'average_fare': row.get('fare_mean')
                })
            
            # Sort by quarter first, then year
            avg_fare_results_sorted = sorted(
                avg_fare_results,
                key=lambda x: (x['quarter'], x['Year'])
            )
            
            # Calculate percentage increase from previous year for each quarter
            # Group by quarter to calculate year-over-year changes
            quarter_data = {}
            for row in avg_fare_results_sorted:
                quarter = row['quarter']
                if quarter not in quarter_data:
                    quarter_data[quarter] = []
                quarter_data[quarter].append(row)
            
            # Add percentage increase column
            final_results = []
            for quarter in sorted(quarter_data.keys()):
                quarter_rows = sorted(quarter_data[quarter], key=lambda x: x['Year'])
                for i, row in enumerate(quarter_rows):
                    if i == 0:
                        # First year for this quarter, no previous year to compare
                        row['percent_increase'] = None
                    else:
                        # Calculate percentage increase from previous year
                        prev_year_fare = quarter_rows[i-1]['average_fare']
                        current_fare = row['average_fare']
                        if prev_year_fare is not None and current_fare is not None and prev_year_fare > 0:
                            percent_increase = ((current_fare - prev_year_fare) / prev_year_fare) * 100
                            row['percent_increase'] = round(percent_increase, 2)
                        else:
                            row['percent_increase'] = None
                    final_results.append(row)
            
            # Display average fare table
            if final_results:
                st.write("**Average Flight Fare by Year and Quarter:**")
                avg_fare_table = MyTable(['Year', 'quarter', 'average_fare', 'percent_increase'], final_results)
                st.dataframe(avg_fare_table.rows, use_container_width=True)
                
                # Calculate average percentage increase for last 5 years and project 2025-2026
                # Find the maximum year in the data
                max_year = max([row['Year'] for row in final_results])
                last_5_years = list(range(max_year - 4, max_year + 1))  # Last 5 years including max_year
                
                # Group by quarter and calculate average percentage increase
                quarter_projections = {}
                for quarter in sorted(quarter_data.keys()):
                    quarter_rows = sorted(quarter_data[quarter], key=lambda x: x['Year'])
                    
                    # Get percentage increases for the last 5 years
                    percent_increases = []
                    for row in quarter_rows:
                        if row['Year'] in last_5_years and row['percent_increase'] is not None:
                            percent_increases.append(row['percent_increase'])
                    
                    # Calculate average percentage increase
                    if percent_increases:
                        avg_percent_increase = sum(percent_increases) / len(percent_increases)
                    else:
                        avg_percent_increase = 0  # Default to 0% if no data
                    
                    # Get the most recent year's fare for this quarter (base for projection)
                    most_recent_row = None
                    for row in reversed(quarter_rows):
                        if row['average_fare'] is not None and row['average_fare'] > 0:
                            most_recent_row = row
                            break
                    
                    if most_recent_row:
                        base_fare = most_recent_row['average_fare']
                        base_year = most_recent_row['Year']
                        
                        # Project 2025 and 2026
                        projections = []
                        
                        # Calculate years to project
                        years_to_project = []
                        years_to_project.append(2025)
                        years_to_project.append(2026)
                        
                        current_fare = base_fare
                        current_year = base_year
                        
                        for proj_year in years_to_project:
                            # Calculate number of years from base year
                            years_diff = proj_year - current_year
                            # Apply average percentage increase for each year
                            projected_fare = current_fare
                            for _ in range(years_diff):
                                projected_fare = projected_fare * (1 + avg_percent_increase / 100)
                            
                            projections.append({
                                'Year': proj_year,
                                'quarter': quarter,
                                'projected_fare': round(projected_fare, 2),
                                'avg_percent_increase': round(avg_percent_increase, 2)
                            })
                            
                            current_fare = projected_fare
                            current_year = proj_year
                        
                        quarter_projections[quarter] = projections
                
                # Store projections for tab3
                if quarter_projections:
                    projection_results = []
                    for quarter in sorted(quarter_projections.keys()):
                        projection_results.extend(quarter_projections[quarter])
                    
                    # Sort by quarter, then year
                    projection_results_sorted = sorted(
                        projection_results,
                        key=lambda x: (x['quarter'], x['Year'])
                    )
                else:
                    projection_results_sorted = []
            else:
                st.info("No average fare data available.")
                projection_results_sorted = []
                final_results = []
        
        with tab3:
            if 'projection_results_sorted' in locals() and projection_results_sorted:
                st.write(f"*Based on average percentage increase from last 5 years ({last_5_years[0]}-{last_5_years[-1]})*")
                projection_table = MyTable(['Year', 'quarter', 'projected_fare', 'avg_percent_increase'], projection_results_sorted)
                st.dataframe(projection_table.rows, use_container_width=True)
                
                # Store in session state for FAQ
                st.session_state.direct_projection_data = projection_results_sorted
            else:
                st.info("No projection data available. Please ensure you have selected both origin and destination cities with direct flights.")
                st.session_state.direct_projection_data = None
    else:
        st.info("No direct routes match the selected criteria.")

    # Indirect flights section
    if selected_origin_city and selected_dest_city:
        st.divider()
        st.subheader("🔄 Indirect Flights (Connecting Route)")
        
        # Filter rows matching origin city -> table_origin
        table_origin = flights.filter(lambda row: row[city1_col] == selected_origin_city)
        
        # Filter rows matching destination city -> table_destination
        table_destination = flights.filter(lambda row: row[city2_col] == selected_dest_city)
        
        if table_origin.rows and table_destination.rows:
            # Rename columns in table_origin to avoid conflicts (add _leg1 suffix to numeric columns)
            origin_renamed_rows = []
            for row in table_origin.rows:
                new_row = row.copy()
                new_row['nsmiles_leg1'] = new_row.get('nsmiles', 0)
                new_row['fare_leg1'] = new_row.get('fare', 0)
                new_row['fare_low_leg1'] = new_row.get('fare_low', 0)
                # Rename city columns to preserve origin city
                new_row['origin_city'] = new_row.get(city1_col)  # Origin city from table_origin
                new_row['connecting_city'] = new_row.get(city2_col)  # This will be used for join
                origin_renamed_rows.append(new_row)
            
            origin_renamed_columns = [col if col not in [city1_col, city2_col] else ('origin_city' if col == city1_col else 'connecting_city') 
                                     for col in table_origin.columns] + ['nsmiles_leg1', 'fare_leg1', 'fare_low_leg1', 'origin_city', 'connecting_city']
            # Remove duplicates
            origin_renamed_columns = list(dict.fromkeys(origin_renamed_columns))
            table_origin_renamed = MyTable(origin_renamed_columns, origin_renamed_rows)
            
            # Rename columns in table_destination to avoid conflicts (add _leg2 suffix to numeric columns)
            dest_renamed_rows = []
            for row in table_destination.rows:
                new_row = row.copy()
                new_row['nsmiles_leg2'] = new_row.get('nsmiles', 0)
                new_row['fare_leg2'] = new_row.get('fare', 0)
                new_row['fare_low_leg2'] = new_row.get('fare_low', 0)
                # Rename city columns to preserve destination city
                new_row['connecting_city_join'] = new_row.get(city1_col)  # This will be used for join
                new_row['destination_city'] = new_row.get(city2_col)  # Destination city from table_destination
                dest_renamed_rows.append(new_row)
            
            dest_renamed_columns = [col if col not in [city1_col, city2_col] else ('connecting_city_join' if col == city1_col else 'destination_city')
                                    for col in table_destination.columns] + ['nsmiles_leg2', 'fare_leg2', 'fare_low_leg2', 'connecting_city_join', 'destination_city']
            # Remove duplicates
            dest_renamed_columns = list(dict.fromkeys(dest_renamed_columns))
            table_destination_renamed = MyTable(dest_renamed_columns, dest_renamed_rows)
            
            # Create a helper: add a join key column to both tables
            # Join key should include: connecting city, Year, and quarter
            origin_with_key_rows = []
            for row in table_origin_renamed.rows:
                new_row = row.copy()
                # Create composite join key: city_year_quarter
                connecting_city = str(row.get('connecting_city', '')).strip()
                year = str(row.get('Year', '')).strip()
                quarter = str(row.get('quarter', '')).strip()
                new_row['join_key'] = f"{connecting_city}_{year}_{quarter}"
                origin_with_key_rows.append(new_row)
            table_origin_with_key = MyTable(table_origin_renamed.columns + ['join_key'], origin_with_key_rows)
            
            dest_with_key_rows = []
            for row in table_destination_renamed.rows:
                new_row = row.copy()
                # Create composite join key: city_year_quarter
                connecting_city = str(row.get('connecting_city_join', '')).strip()
                year = str(row.get('Year', '')).strip()
                quarter = str(row.get('quarter', '')).strip()
                new_row['join_key'] = f"{connecting_city}_{year}_{quarter}"
                dest_with_key_rows.append(new_row)
            table_destination_with_key = MyTable(table_destination_renamed.columns + ['join_key'], dest_with_key_rows)
            
            # Join on the join_key (connecting_city + Year + quarter from origin = connecting_city_join + Year + quarter from destination)
            indirect_flights = table_origin_with_key.join(table_destination_with_key, on='join_key', how='inner')
            
            # Add nsmiles, fare, and fare_low from both legs to calculate totals
            rows_with_totals = []
            for row in indirect_flights.rows:
                new_row = row.copy()
                # Add the values from both legs
                nsmiles_leg1 = new_row.get('nsmiles_leg1', 0) or 0
                nsmiles_leg2 = new_row.get('nsmiles_leg2', 0) or 0
                fare_leg1 = new_row.get('fare_leg1', 0) or 0
                fare_leg2 = new_row.get('fare_leg2', 0) or 0
                
                new_row['nsmiles_total'] = nsmiles_leg1 + nsmiles_leg2
                new_row['fare_total'] = fare_leg1 + fare_leg2
                rows_with_totals.append(new_row)
            
            # Create a temporary table with all rows (including totals)
            temp_table_all = MyTable(
                indirect_flights.columns + ['nsmiles_total', 'fare_total'],
                rows_with_totals
            )
            
            # Use filter() to keep only rows where both legs have valid fare prices
            temp_table = temp_table_all.filter(lambda row: 
                isinstance(row.get('fare_leg1'), (int, float)) and row.get('fare_leg1', 0) > 0 and
                isinstance(row.get('fare_leg2'), (int, float)) and row.get('fare_leg2', 0) > 0
            )
            
            # Group by Year and quarter, get closest route (lowest nsmiles_total) for each combination
            if temp_table.rows:
                # Use groupby to group by Year and quarter
                grouped = temp_table.groupby(['Year', 'quarter'])
                
                # For each group, use filter() to find the closest route (lowest nsmiles_total, then lowest fare_total)
                closest_rows_per_year_quarter = []
                for (year, quarter), group_rows in grouped.groups.items():
                    # Create a MyTable for this group
                    group_table = MyTable(temp_table.columns, group_rows)
                    
                    # Find the minimum nsmiles_total in this group
                    min_nsmiles = min([float(row.get('nsmiles_total', 0) or 0) for row in group_rows])
                    
                    # Filter to only rows with the minimum nsmiles_total
                    rows_with_min_nsmiles = group_table.filter(lambda row: float(row.get('nsmiles_total', 0) or 0) == min_nsmiles)
                    
                    # If multiple rows have the same minimum nsmiles_total, find the minimum fare_total
                    if len(rows_with_min_nsmiles.rows) > 1:
                        min_fare = min([float(row.get('fare_total', 0) or 0) for row in rows_with_min_nsmiles.rows])
                        # Filter to only rows with minimum fare_total (use small epsilon for floating point comparison)
                        closest_rows = rows_with_min_nsmiles.filter(lambda row: abs(float(row.get('fare_total', 0) or 0) - min_fare) < 0.01)
                        # Take the first one (they're all equivalent)
                        if closest_rows.rows:
                            closest_rows_per_year_quarter.append(closest_rows.rows[0])
                    else:
                        # Only one row with minimum nsmiles_total
                        if rows_with_min_nsmiles.rows:
                            closest_rows_per_year_quarter.append(rows_with_min_nsmiles.rows[0])
                
                # Create a clean joined table showing: origin city (from table_origin), destination city (from table_destination), and totals
                clean_rows = []
                for row in closest_rows_per_year_quarter:
                    # Get connecting airport - use airport_2 from leg1 (destination airport of first leg)
                    # This is the airport at the connecting city
                    connecting_airport = row.get(airport2_col, '')  # From leg1, this is the connecting airport
                    # If not available, try airport_1 from leg2 (should be the same)
                    if not connecting_airport:
                        connecting_airport = row.get(airport1_col, '')
                    
                    clean_row = {
                        'Year': row.get('Year'),
                        'quarter': row.get('quarter'),
                        'origin_city': row.get('origin_city'),  # From table_origin
                        'connecting_city': row.get('connecting_city'),  # The city they joined on
                        'connecting_airport': connecting_airport,  # The airport at the connecting city
                        'destination_city': row.get('destination_city'),  # From table_destination
                        'nsmiles_total': row.get('nsmiles_total', 0),
                        'fare_total': row.get('fare_total', 0)
                    }
                    clean_rows.append(clean_row)
                
                # Create final table with selected columns
                display_columns = ['Year', 'quarter', 'origin_city', 'connecting_city', 'connecting_airport', 'destination_city', 'nsmiles_total', 'fare_total']
                joined_table_display = MyTable(display_columns, clean_rows)
                
                if joined_table_display.rows:
                    total_count = len(rows_with_totals)
                    displayed_count = len(closest_rows_per_year_quarter)
                    
                    # Create tabs for indirect flights
                    tab_indirect1, tab_indirect2, tab_indirect3 = st.tabs(["Indirect Flights Table", "Flight Fare by Year/Quarter", "Projections 2025-2026"])
                    
                    with tab_indirect1:
                        st.write(f"**Joined Table: {total_count} connecting route record(s) found (showing closest route per year-quarter, {displayed_count} total)**")
                        st.dataframe(joined_table_display.rows, use_container_width=True)
                        
                        # Create line chart for indirect flights
                        import plotly.graph_objects as go
                        
                        # Prepare data for chart - create time series from Year and quarter
                        chart_data = []
                        for row in clean_rows:
                            # Create a time label from Year and quarter
                            time_label = f"{row['Year']}-Q{row['quarter']}"
                            chart_data.append({
                                'time': time_label,
                                'Year': row['Year'],
                                'quarter': row['quarter'],
                                'fare_total': row['fare_total'] if row['fare_total'] is not None else 0
                            })
                        
                        # Sort by Year and quarter for proper time series
                        chart_data_sorted = sorted(chart_data, key=lambda x: (x['Year'], x['quarter']))
                        
                        # Store indirect flight chart data for combined chart
                        indirect_flight_chart_data = chart_data_sorted
                    
                    with tab_indirect2:
                        # Projection Analysis: Sort by quarter ascending, then year
                        indirect_sorted = sorted(
                            clean_rows,
                            key=lambda x: (x['quarter'], x['Year'])
                        )
                        
                        # Group by quarter to calculate year-over-year percentage increase
                        quarter_indirect_data = {}
                        for row in indirect_sorted:
                            quarter = row['quarter']
                            if quarter not in quarter_indirect_data:
                                quarter_indirect_data[quarter] = []
                            quarter_indirect_data[quarter].append(row)
                        
                        # Calculate percentage increase for each quarter
                        indirect_projection_results = []
                        for quarter in sorted(quarter_indirect_data.keys()):
                            quarter_rows = sorted(quarter_indirect_data[quarter], key=lambda x: x['Year'])
                            for i, row in enumerate(quarter_rows):
                                if i == 0:
                                    # First year for this quarter, no previous year to compare
                                    percent_increase = None
                                else:
                                    # Calculate percentage increase from previous year
                                    prev_year_fare = quarter_rows[i-1]['fare_total']
                                    current_fare = row['fare_total']
                                    if prev_year_fare is not None and current_fare is not None and prev_year_fare > 0:
                                        percent_increase = ((current_fare - prev_year_fare) / prev_year_fare) * 100
                                        percent_increase = round(percent_increase, 2)
                                    else:
                                        percent_increase = None
                                
                                indirect_projection_results.append({
                                    'Year': row['Year'],
                                    'quarter': row['quarter'],
                                    'total_fare': row['fare_total'],
                                    'percent_increase': percent_increase
                                })
                        
                        # Display indirect flight projection table
                        if indirect_projection_results:
                            st.write("**Indirect Flight Fare Analysis:**")
                            indirect_proj_table = MyTable(['Year', 'quarter', 'total_fare', 'percent_increase'], indirect_projection_results)
                            st.dataframe(indirect_proj_table.rows, use_container_width=True)
                        else:
                            st.info("No indirect flight data available for projection analysis.")
                    
                    with tab_indirect3:
                        # Project 2025 and 2026 using last 5 years of data
                        # Find the maximum year in the data
                        max_year = max([row['Year'] for row in clean_rows])
                        last_5_years = list(range(max_year - 4, max_year + 1))  # Last 5 years including max_year
                        
                        # Group by quarter and calculate average percentage increase
                        quarter_projections = {}
                        for quarter in sorted(quarter_indirect_data.keys()):
                            quarter_rows = sorted(quarter_indirect_data[quarter], key=lambda x: x['Year'])
                            
                            # Get percentage increases for the last 5 years
                            percent_increases = []
                            for row in quarter_rows:
                                if row['Year'] in last_5_years:
                                    # Calculate percentage increase from previous year
                                    prev_row = None
                                    for prev in quarter_rows:
                                        if prev['Year'] == row['Year'] - 1:
                                            prev_row = prev
                                            break
                                    
                                    if prev_row and prev_row['fare_total'] is not None and row['fare_total'] is not None and prev_row['fare_total'] > 0:
                                        percent_increase = ((row['fare_total'] - prev_row['fare_total']) / prev_row['fare_total']) * 100
                                        percent_increases.append(percent_increase)
                            
                            # Calculate average percentage increase
                            if percent_increases:
                                avg_percent_increase = sum(percent_increases) / len(percent_increases)
                            else:
                                avg_percent_increase = 0  # Default to 0% if no data
                            
                            # Get the most recent year's fare for this quarter (base for projection)
                            most_recent_row = None
                            for row in reversed(quarter_rows):
                                if row['fare_total'] is not None and row['fare_total'] > 0:
                                    most_recent_row = row
                                    break
                            
                            if most_recent_row:
                                base_fare = most_recent_row['fare_total']
                                base_year = most_recent_row['Year']
                                
                                # Project 2025 and 2026
                                projections = []
                                
                                # Calculate years to project
                                years_to_project = []
                                if 2025 > base_year:
                                    years_to_project.append(2025)
                                if 2026 > base_year:
                                    years_to_project.append(2026)
                                
                                current_fare = base_fare
                                current_year = base_year
                                
                                for proj_year in years_to_project:
                                    # Calculate number of years from base year
                                    years_diff = proj_year - current_year
                                    # Apply average percentage increase for each year
                                    projected_fare = current_fare
                                    for _ in range(years_diff):
                                        projected_fare = projected_fare * (1 + avg_percent_increase / 100)
                                    
                                    projections.append({
                                        'Year': proj_year,
                                        'quarter': quarter,
                                        'projected_fare': round(projected_fare, 2),
                                        'avg_percent_increase': round(avg_percent_increase, 2)
                                    })
                                    
                                    current_fare = projected_fare
                                    current_year = proj_year
                                
                                quarter_projections[quarter] = projections
                        
                        # Create projection table
                        if quarter_projections:
                            projection_results = []
                            for quarter in sorted(quarter_projections.keys()):
                                projection_results.extend(quarter_projections[quarter])
                            
                            # Sort by quarter, then year
                            projection_results_sorted = sorted(
                                projection_results,
                                key=lambda x: (x['quarter'], x['Year'])
                            )
                            
                            st.write(f"**Projected Indirect Flight Fares for 2025 and 2026**")
                            st.write(f"*Based on average percentage increase from last 5 years ({last_5_years[0]}-{last_5_years[-1]})*")
                            indirect_projection_table = MyTable(['Year', 'quarter', 'projected_fare', 'avg_percent_increase'], projection_results_sorted)
                            st.dataframe(indirect_projection_table.rows, use_container_width=True)
                            
                            # Store in session state for FAQ
                            st.session_state.indirect_projection_data = projection_results_sorted
                        else:
                            st.info("No projection data available. Please ensure you have indirect flight data.")
                            st.session_state.indirect_projection_data = None
                else:
                    st.info("No indirect routes found with connecting flights.")
                    indirect_flight_chart_data = None
            else:
                st.info("No indirect routes found with connecting flights.")
                indirect_flight_chart_data = None
        else:
            if not table_origin.rows:
                st.info(f"No flights found departing from {selected_origin_city}.")
            if not table_destination.rows:
                st.info(f"No flights found arriving at {selected_dest_city}.")
            indirect_flight_chart_data = None
    

if __name__ == "__main__":
    main()