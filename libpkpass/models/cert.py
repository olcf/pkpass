from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.schema import Column
from libpkpass.models import Base

class Cert(Base):
    """Table of Certificates"""
    __tablename__ = 'cert'
    cert_bytes = Column(String())
    verified = Column(Boolean)
    fingerprint = Column(String(), primary_key=True)
    subject = Column(String())
    issuer = Column(String())
    enddate = Column(DateTime())
    issuerhash = Column(String())
    subjecthash = Column(String())

        #########################################
    def __repr__(self):
        #########################################
        return f"<Cert {self.fingerprint}>"

    def __iter__(self):
        for c in self.__table__.columns:
            yield c.name, getattr(self, c.name)
