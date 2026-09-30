FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instala interface gráfica leve e utilitários
RUN apt-get update && apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 3000

CMD ["/bin/bash"]