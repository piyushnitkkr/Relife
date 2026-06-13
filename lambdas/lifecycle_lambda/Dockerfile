FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy handler and model (if pre-trained)
COPY handler.py .
# COPY model/ ./model/

CMD ["handler.lambda_handler"]
