library(cluster)
library(plotly)

# Fill these in
pairwise_edit_distance_dir <- "example/out/pairwise_edit_distance_2.csv"
output_file <- "example/out/k-medoids_clustering_2.csv"
num_clusters <- 4
dimensions <- 3  # 2 or 3. For multi-dimensional scaling - does not affect PAM


df <- read.csv(pairwise_edit_distance_dir, header = TRUE, row.names = 1)
d <- dist(df, 'euclidean')
p <- pam(df, num_clusters, TRUE)

write.csv(as.data.frame(p$clustering), file = output_file)

s <- cmdscale(df, dimensions)

c <- as.data.frame(cbind(s, p$clustering))

colors <- c("#999999", "#E69F00", "#56B4E9", "#009E73",
            "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

if (dimensions == 2) {
  fig <- plot_ly(x = c[, 1], y = c[, 2],
                 color = c[, 3], colors = colors,
                 type = "scatter", mode = "markers",
                 text = paste('Participant: ', rownames(c), ', clust:', c[, 3]),
  ) %>% hide_colorbar()
}else {
  fig <- plot_ly(x = c[, 1], y = c[, 2], z = c[, 3],
                 color = c[, 4], colors = colors,
                 type = 'scatter3d', mode = 'markers',
                 text = paste('Participant: ', rownames(c), ', clust:', c[, 4]),
  ) %>% hide_colorbar()
}
fig
