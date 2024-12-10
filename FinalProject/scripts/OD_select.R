library(tidyverse)
library(tmap)
library(stplanr)

library(sf)

library(tmap)
library(basemaps)
library(lehdr) # package to download and process lehd data
library(tigris) # package to download any census geography shapefiles; we will need it for mapping 

# set the wd as the folder where the script is located
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
getwd()

# read the census blocks from csv
aa_blocks = read.csv("../outputs/aa_blocks.csv")
# get a list of the block codes
block_codes = aa_blocks$GEOID20

# get the lobes data
aa_lodes = grab_lodes(state = "mi", year = 2021, lodes_type = "od", state_part = "main", agg_geo = "block")

# filter the lodes data to only include the block codes we are interested in
aa_lodes_1 = aa_lodes %>% filter(w_geocode %in% block_codes & h_geocode %in% block_codes)

# save as aa_lodes_cleaned.csv
write.csv(aa_lodes_1, "../outputs/aa_lodes_cleaned.csv", row.names = FALSE)

# see the length of the data with S000 greater than 10
aa_lodes_1 %>% filter(S000 > 20) %>% nrow()

# now we create a map showing the most common OD Blocks and the lines between them

# first, filter the data to only include the most common OD blocks
aa_lodes_2 = aa_lodes_1 %>% filter(S000 > 20)

# get the list of the most common OD blocks, both as origin and destination
common_blocks = unique(c(aa_lodes_2$w_geocode, aa_lodes_2$h_geocode))

# read the census blocks shapefile
blocks = tigris::blocks(state = "MI")

# filter the blocks shapefile to only include the common blocks
blocks = blocks %>% filter(GEOID20 %in% common_blocks)

# get centroids of the blocks
blocks_centroids = st_centroid(blocks) %>% select(GEOID20, geometry)
commute = od2line(aa_lodes_2, blocks_centroids)

brks = round(quantile(commute$S000, probs=c(0, 0.5, 0.8, 0.95, 1)), 0)

commute = commute %>% mutate(
  Volume = case_when(
    S000 >= brks[1] & S000 <= brks[2] ~ 0.1,
    S000 > brks[2] & S000 <= brks[3] ~ 0.2,
    S000 > brks[3] & S000 <= brks[4] ~ 0.5,
    S000 > brks[4] & S000 <= brks[5] ~ 1
  )
)

set_defaults(map_service = "carto", map_type = "light")
# determine the bounding box of the basemap based on data 
bgbox = st_bbox(blocks) %>% st_as_sfc()
# retrieve basemap as a raster 
bg = basemap_stars(bgbox)

# plot the map
tmap_mode('plot')
tm_shape(bg) + 
  tm_rgb() + 
  tm_shape(blocks) + 
  tm_polygons(alpha=0) + 
  # sort by volume in ascending order so that thicker lines are drawn last 
  tm_shape(commute %>% arrange(Volume)) + 
  tm_lines(col='S000', lwd='S000', scale=10, style="quantile", 
           palette=c("#091c58", "#243394", "#215fa8", "#1e91be"),
           legend.col.show = F, legend.lwd.show = F) + 
  # create manual legend 
  tm_add_legend(type=c("line"), labels=c("21-28", "28-41", "41-58", "58-98"), 
                col=c("#091c58", "#243394", "#215fa8", "#1e91be"),
                lwd=c(0.1, 0.2, 0.5, 1) * 10,
                title="Number of Commuters") + 
  # add north compass 
  tm_compass() + 
  # add scale bar 
  tm_scale_bar() + 
  # add plot title
  tm_layout(main.title = "Popular Commute Flow in Ann Arbor")

# load the UM blocks
um_blocks = read.csv("../outputs/UM_Campus_Blocks.csv")

# filter lobes data to only origin in UM blocks
aa_lodes_3 = aa_lodes_1 %>% filter(w_geocode %in% um_blocks$GEOID20)
# filter for the most common OD blocks
aa_lodes_3 = aa_lodes_3 %>% filter(S000 > 1)

common_blocks = unique(c(aa_lodes_3$w_geocode, aa_lodes_3$h_geocode))

blocks = tigris::blocks(state = "MI")
blocks = blocks %>% filter(GEOID20 %in% common_blocks)

blocks_centroids = st_centroid(blocks) %>% select(GEOID20, geometry)
commute = od2line(aa_lodes_3, blocks_centroids)

brks = round(quantile(commute$S000, probs=c(0, 0.5, 0.8, 0.95, 1)), 0)

commute = commute %>% mutate(
  Volume = case_when(
    S000 >= brks[1] & S000 <= brks[2] ~ 0.1,
    S000 > brks[2] & S000 <= brks[3] ~ 0.2,
    S000 > brks[3] & S000 <= brks[4] ~ 0.5,
    S000 > brks[4] & S000 <= brks[5] ~ 1
  )
)

set_defaults(map_service = "carto", map_type = "light")
bgbox = st_bbox(blocks) %>% st_as_sfc()

bg = basemap_stars(bgbox)

tmap_mode('plot')

tm_shape(bg) + 
  tm_rgb() + 
  tm_shape(blocks) + 
  tm_polygons(alpha=0) + 
  tm_shape(commute %>% arrange(Volume)) + 
  tm_lines(col='S000', lwd='S000', scale=10, style="quantile", 
           palette=c("#091c58", "#243394", "#215fa8", "#1e91be"),
           legend.col.show = F, legend.lwd.show = F) + 
  tm_add_legend(type=c("line"), labels=c("2", "2-3", "3-5", "5-10"), 
                col=c("#091c58", "#243394", "#215fa8", "#1e91be"),
                lwd=c(0.1, 0.2, 0.5, 1) * 10,
                title="Number of Commuters") + 
  tm_compass() + 
  tm_scale_bar() + 
  tm_layout(main.title = "Popular Commute Flow for workers in UM Campus")
