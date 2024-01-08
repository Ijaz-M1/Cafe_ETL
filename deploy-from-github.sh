set -eu

#### CONFIGURATION SECTION ####
team_name="Mario's Espresso Pipeline"
deployment_bucket="marios-espresso-pipeline-deployment-bucket"
app_bucket="marios-espresso-pipeline-etl-app"

#### CONFIGURATION SECTION ####

# Create deployment bucket stack
echo ""
echo "Doing deployment bucket..."
aws cloudformation deploy --stack-name ${deployment_bucket} \
    --template-file deployment-bucket-stack.yml --region eu-west-1 \
    --capabilities CAPABILITY_IAM;

# Install dependencies from requirements-deploy.txt into src directory with python 3.9
# On windows use `py` not `python3`
echo ""
echo "Doing pip install..."
python3 -m pip install --platform manylinux2014_x86_64 \
    --target=./src --implementation cp --python-version 3.9 \
    --only-binary=:all: --upgrade -r requirements-lambda.txt;


# finishing the deployment
echo ""
echo "...all done!"
echo ""
