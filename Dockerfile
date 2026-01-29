# Use dumb-init for proper signal handling
RUN apt-get install -y dumb-init
ENTRYPOINT ["dumb-init", "--"]
CMD ["python", "-m", "gateway.main"]
