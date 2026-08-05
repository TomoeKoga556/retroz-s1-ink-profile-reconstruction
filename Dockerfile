FROM python:3.12-slim
WORKDIR /workspace
COPY . .
RUN python -m pip install --no-cache-dir .
ENTRYPOINT ["python", "-m", "retroz_s1"]
CMD ["list-candidates"]
