from matplotlib import pyplot as plt
import pandas as pd

# Load the CSV files
network_attr_nodes = pd.read_csv('./temp/network_attr_nodes.csv')
spatial_properties = pd.read_csv('./temp/stops_arcgis_outputtable.csv')

# Merge the dataframes on the 'Id' column
# network_attr_nodes.Id = spatial_properties.stop_id
merged_df = pd.merge(network_attr_nodes, spatial_properties, left_on='Id', right_on='stop_id')

# create a scatter plot with degree on the x-axis, and distance to city center on the y-axis
# give the points colors based on their degree
# reverse the color map so that higher degrees are darker
# set the opacity of the points to 0.5
plt.scatter(merged_df['Degree'], merged_df['dist_ctr'], c=merged_df['Degree'], cmap='viridis_r', alpha=0.8)
# title
plt.title('Degree vs Distance to City Center')
# x-axis label
plt.xlabel('Degree')
# y-axis label
plt.ylabel('Distance to City Center (m)')
# label the points with degree > 7
for i, stop_name in enumerate(merged_df['stop_name']):
    if merged_df['Degree'][i] > 7:
        # offset the text so that the center of the text is at the point
        plt.text(merged_df['Degree'][i], merged_df['dist_ctr'][i], stop_name, fontsize=6, ha='center', va='center')

# Save the plot to a file
plt.savefig('./temp/degree_vs_distance.png')