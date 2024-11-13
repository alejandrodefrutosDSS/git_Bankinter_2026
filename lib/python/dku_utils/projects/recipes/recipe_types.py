VISUAL_RECIPES = [
     "sync", # Sync
     "shaker", # Prepare
     "sampling", # Filter
     "grouping", # Group
     "distinct", # Distinct
     "window", # Window
     "join", # Join with...
     "fuzzyjoin", # Fuzzy join
     "geojoin", # Geo join
     "split", # Split
     "topn", # Top N
     "sort", # Sort
     "pivot", # Pivot
     "vstack", # Stack
     "generate_features" # Generate features
     ]


CODE_RECIPES = [
      "python", # Python
      "r", # R
      "sql_query", # SQL/Query
      "sql_script", # SQL/Script
      "shell", # Shell
      "spark_sql_query", # Spark SQL
      "spark_scala", # Spark Scala
      "pyspark", # PySpark
      "sparkr", # Spark R
      "cpython", # Streaming Python
      "streaming_spark_scala" # Streaming Spark
      ]


OTHER_RECIPES = [
      "clustering_cluster", # Scoring recipes for clustering tasks. Their input is a dataset to score and their output is a scored dataset.
      "clustering_training", # Training recipes for clustering tasks. Their input is the dataset associated to the initial ML Task and their output is a deployed "Clustering" model.
      "clustering_scoring", # Scoring recipes for clustering tasks. Their input is a deployed "Clustering" model and their output is a scored dataset.
      "prediction_training", # Training recipes for 'Regression', 'Classification', 'Deep Learning Prediction', 'Visual Time Series', and 'Causal ML models' tasks.
      "prediction_scoring", # Scoring recipes for 'Regression', 'Classification', 'Deep Learning Prediction', 'Visual Time Series', and 'Causal ML models' tasks.
      "evaluation", # Evaluation recipes.
      "export", # xport to folder
      "update" # Push to editable
      ]