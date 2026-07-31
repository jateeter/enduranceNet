FROM eclipse-temurin:21-jdk AS builder

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://github.com/sbt/sbt/releases/download/v1.9.9/sbt-1.9.9.tgz | tar xz -C /usr/local && \
    ln -s /usr/local/sbt/bin/sbt /usr/local/bin/sbt

WORKDIR /app

COPY build.sbt .
COPY project/ project/

RUN sbt update

COPY app/ app/
COPY conf/ conf/
COPY public/ public/

RUN sbt stage

FROM eclipse-temurin:21-jre

WORKDIR /app

COPY --from=builder /app/target/universal/stage/ .

ENV APPLICATION_SECRET="changeme_replace_in_production"
ENV JAVA_OPTS="-Xmx512m -Xms256m"

EXPOSE 9000

ENTRYPOINT ["./bin/endurancenet-backend"]
