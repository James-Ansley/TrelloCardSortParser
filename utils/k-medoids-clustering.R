require(graphics)
library(cluster)

# Fill these in
pairwise_edit_distance_dir <- "resources/out/pairwise_edit_distance_1.csv"
num_clusters <- 2


df <- read.csv(pairwise_edit_distance_dir, header = TRUE, row.names = 1)
d <- dist(df, 'euclidean')
p <- pam(df, num_clusters, TRUE)

s <- cmdscale(df, 2)

x <- s[,1]
y <- s[,2]
plot(x, y, type = "n", xlab = "", ylab = "", asp = 1, axes = FALSE)
text(x, y, rownames(s))

# Returns the clusters resulting from partitioning around num_clusters medoids
p$clustering
