FROM python:3.12-slim
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY main.py /app/main.py
USER appuser
EXPOSE 8080
ENV PORT=8080 APP_VERSION=1.0.0
CMD ["python", "-u", "/app/main.py"]
