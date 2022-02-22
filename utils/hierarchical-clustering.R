library(ggplot2)

# Fill these in
co_occurrence_distance_dir <- "example/out/co_distance_matrix_1.csv"
output_file <- "example/out/hclust_1.csv"
title <- "Sort 1: HCA(method='complete')"
num_clusters <- 3


df <- read.csv(co_occurrence_distance_dir, header = TRUE, row.names = 1)
d <- dist(df, 'euclidean')
hc <- hclust(d, method = "complete", members = NULL)

par(mar = c(1, 4, 4, 2))
plot(hc, main = title, ylab = 'Distance', sub = '', xlab = '')

clusts <- cutree(hc, k = num_clusters, h = NULL)
write.csv(as.data.frame(clusts), file = output_file)

# Include this if you want a zany and exciting dotted line to be drawn on the
# dendrogram cutting it into num_clusters clusters

# cut_point <- nrow(df) - num_clusters
# mid_point <- (hc$height[cut_point] + hc$height[cut_point + 1]) / 2
# abline(h = mid_point, lty = 2)
