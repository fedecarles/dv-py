from constraints import StandardConstraints
import pandas as pd

data_old = pd.read_csv(r"brain_stroke.csv") # load csv into pandas

# Generate constraints
constraints = StandardConstraints() # create contraints object
constraints.generate_constraints(data_new) # generate contraints for the dataframe
print(constraints)

# Modify constraints
constraints.modify_constraint("gender", {"data_type": "category"}) 
constraints.modify_constraint("work_type", {"data_type": "category", "nullable": False}) 
constraints.modify_constraint("age", {"max_value": 80}) 
constraints.modify_constraint("date", {"data_type": "datetime64[ns]"}) 

# Save constraints
constraints.save_as("example_constraints.json") 

# Validate data

from verifiers import StandardVerifier

data_new = pd.read_csv(r"test_data/brain_stroke.csv") # load new data into pandas

# Read constraints from json
constraints = StandardConstraints().read_constraints("example_constraints.json")

# Generate summary and detail reports
verify = StandardVerifier(data_new, constraints, enforce_dtypes=True)
print(verify.validation_summary)
print(verify.validation_data)
