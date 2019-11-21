FROM mgorny/gentoo-python
WORKDIR /gentoopm
COPY . /gentoopm
RUN ["tox"]
CMD ["./gentoopmq"]
