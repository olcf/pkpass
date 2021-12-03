from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from libpkpass.models import Base

recipient_cert = Table(
    'recipient_cert', Base.metadata,
    Column('recipient_name', String(), ForeignKey('recipient.name')),
    Column('cert_fingerprint', String(), ForeignKey('cert.fingerprint')),
)

class Recipient(Base):
    """table of health status of services"""
    __tablename__ = 'recipient'
    name = Column(String(), primary_key=True)
    key = Column(String(), nullable=True)
    certs = relationship("Cert", secondary=recipient_cert, backref='recipients', lazy='joined')

        #########################################
    def __repr__(self):
        #########################################
        return f"<Recipient {self.name}>"

    def __iter__(self):
        for c in self.__table__.columns:
            yield c.name, getattr(self, c.name)
