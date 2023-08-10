ARG python_ver=3.9
FROM python:${python_ver}

ARG netbox_ver=v3.3.10
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN groupadd -g 1000 netbox && useradd -m -u 1000 -g netbox netbox
RUN mkdir -p /opt/netbox /source && chown netbox:netbox /opt/netbox /source
USER netbox

# -------------------------------------------------------------------------------------
# Install NetBox
# -------------------------------------------------------------------------------------
RUN git clone --single-branch --branch ${netbox_ver} https://github.com/netbox-community/netbox.git /opt/netbox/ && \
    cd /opt/netbox/ && \
    pip install -r /opt/netbox/requirements.txt

# Work around https://github.com/rq/django-rq/issues/421
RUN pip install django-rq==2.3.2

# Workaround for https://github.com/netbox-community/netbox/issues/12415 (our current version is also impacted)
# to remove once django-rq is bumped to >= 2.8.0d)
RUN pip install rq==1.13.0

# -------------------------------------------------------------------------------------
# Install Netbox Plugins
# -------------------------------------------------------------------------------------
WORKDIR /source
COPY --chown=netbox:netbox . /source

RUN ./develop/setup-plugins.sh

WORKDIR /opt/netbox/netbox/
