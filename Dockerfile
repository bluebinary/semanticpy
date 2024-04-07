# syntax = docker/dockerfile:1.4.0

FROM python:3.11

# Copy the requirements and install them
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy the tests into the container
COPY ./tests /tests

# Copy the library source into the container's source folder for black lint checking
COPY ./source/semanticpy /source/semanticpy

# Copy the library source into the container's site-packages folder for running unit tests
COPY ./source/semanticpy /usr/local/lib/python3.11/site-packages/semanticpy

# Create a custom entry point that allows us to override the command as needed
COPY <<"EOF" /entrypoint.sh
#!/bin/bash
ARGS=( "$@" );

if [[ "${ARGS[0]}" == "black" ]]; then
	black ${ARGS[@]:1}
elif [[ "${ARGS[0]}" == "pytest" ]]; then
	pytest /tests ${ARGS[@]:1}
else
	pytest /tests ${ARGS[@]:1}
fi
EOF

RUN chmod +x /entrypoint.sh

# Run the unit tests starter shell script
ENTRYPOINT [ "/entrypoint.sh" ]
