library(ggplot2)

# Fill these in
co_occurrence_distance_dir <- "resources/out/co_distance_matrix_1.csv"
title <- "Sort 1: HCA(method='complete')"
num_clusters <- 2


df <- read.csv(co_occurrence_distance_dir, header = TRUE, row.names = 1)
d <- dist(df, 'euclidean')
hc <- hclust(d, method = "complete", members = NULL)

par(mar = c(1, 4, 4, 2))
plot(hc, main = title, ylab = 'Distance', sub = '', xlab = '')

# Returns the clusters resulting from cutting the dendrogram into num_clusters
# clusters
cutree(hc, k = num_clusters, h = NULL)


# Include this if you want a zany and exciting dotted line to be drawn on the
# dendrogram cutting it into num_clusters clusters

# cut_point <- nrow(df) - num_clusters
# mid_point <- (hc$height[cut_point] + hc$height[cut_point + 1]) / 2
# abline(h = mid_point, lty = 2)
