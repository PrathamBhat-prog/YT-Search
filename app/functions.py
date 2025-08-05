import numpy as np 
import polars
from scipy.spatial.distance import cityblock

# helper function
def returnSearchResultIndexes(query: str, 
                        df: polars.lazyframe.frame.LazyFrame, 
                        model, 
                        dist_func) -> np.ndarray:
    """
        Function to return indexes of top search results
    """
    
    # embed query
    query_embedding = model.encode(query)

    # Collect the dataframe now to access embeddings
    df_collected = df.collect()

    # Extract title+transcript embeddings
    embed_1 = df_collected.select(df_collected.columns[4:388]).to_numpy()
    embed_2 = df_collected.select(df_collected.columns[388:]).to_numpy()

    # Compute cityblock (manhattan) distances manually
    dist_arr = np.array([
        dist_func(query_embedding, e1) + dist_func(query_embedding, e2)
        for e1, e2 in zip(embed_1, embed_2)
    ])

    # search parameters
    threshold = 40  # eyeballed threshold for manhattan distance
    top_k = 5

    # evaluate videos close to query based on threshold
    idx_below_threshold = np.argwhere(dist_arr.flatten() < threshold).flatten()
    idx_sorted = np.argsort(dist_arr[idx_below_threshold], axis=0).flatten()

    # return indexes of search results
    return idx_below_threshold[idx_sorted][:top_k]
