FROM python:3.6.4-alpine3.7
MAINTAINER Shane Frasier <jeremy.frasier@beta.dhs.gov>

# Install shadow so we have adduser and addgroup.  This is a build
# dependency that will be removed at the end.
#
# I also reinstall wget with openssl, since otherwise wget does not
# seem to know how to HTTPS.
RUN apk --no-cache add openssl shadow wget

# Update pip and setuptools
RUN pip3 install --upgrade pip setuptools

# Install cyhy-mailer
RUN mkdir cyhy-mailer \
    && wget -q -O - https://api.github.com/repos/dhs-ncats/cyhy-mailer/tarball | tar xz --strip-components=1 -C cyhy-mailer \
    && pip3 install --upgrade ./cyhy-mailer

# Create unprivileged user
ENV MAILER_HOME=/home/mailer
RUN mkdir ${MAILER_HOME} \
    && addgroup -S mailer \
    && adduser -S -g "Mailer user" -G mailer mailer \
    && chown -R mailer:mailer ${MAILER_HOME}

# Remove build dependencies
RUN apk --no-cache del shadow

# Prepare to Run
WORKDIR MAILER_HOME
USER mailer:mailer
ENTRYPOINT ["cyhy-mailer"]
CMD ["--help"]
