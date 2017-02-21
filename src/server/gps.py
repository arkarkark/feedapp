# Copyright 2017 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import os
import logging
import datetime
import urllib
import json
import StringIO

from PIL import Image, ImageDraw, ImageFont

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email import Encoders


from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api.mail import InboundEmailMessage

from google.appengine.api import images

from oauth2client.contrib.appengine import AppAssertionCredentials

import auth

from wtwf import wtwfhandler
from wtwf.WtwfModel import WtwfNdbModel

from crud import crud_model
from crud import crud_handler

class PictureMail(crud_model.CrudNdbModel):
  """Info and options about a picture mail email address"""

  name = ndb.StringProperty()
  # automatic fields
  created = ndb.DateTimeProperty(auto_now_add=True)

class PictureMailItem(crud_model.CrudNdbModel):
  """Stores Info about a post to a feed."""

  parent_model_name = 'MailFeed'

  subject = ndb.StringProperty()
  body = ndb.TextProperty()
  guid = ndb.StringProperty()
  # automatic fields
  created = ndb.DateTimeProperty(auto_now_add=True)

class EmailToPicture(InboundMailHandler):

  def post(self, name):
    """Transforms body to email request."""

    try:
      name = urllib.unquote(name).split('@')[0]
    except:
      pass

    # get the feed object
    picture_mail = PictureMail.query(PictureMail.name == name).get()
    if picture_mail is not None:
      self.receive(mail.InboundEmailMessage(self.request.body), feed)
    else:
      # 404 ?
      pass

  def receive(self, mail_message, feed):

    sender = mail_message.sender

    if sender:
      # strip it just to the domain name
      try:
        sender = sender.split("@")[1].split(".")[-2]
      except IndexError:
        pass

    subject = mail_message.subject
    if sender:
      subject = ": ".join([sender, subject])
    body = mail_message.bodies().next()[1].decode()

    logging.info("Subject is : %r", subject)
    logging.debug("Body is : %r", body)

    item = MailFeedItem(parent=feed.key, subject=subject, body=body)
    item.put()

    logging.info("Added a message for: " + feed.name)

class Demo(webapp.RequestHandler):
  """Setup a Demo feed."""

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'

    file_name = os.path.join(os.path.dirname(__file__), 'original_msg.txt')
    message = mail.InboundEmailMessage(open(file_name, 'r').read())

    if False:
      for content_type, body in message.bodies():
        self.response.out.write("body %r\n" % [content_type, body.decode()])

    for attachment in message.attachments:
      image_data = attachment.payload.decode()
      img = images.Image(image_data=image_data)
      img.rotate(0)
      img.execute_transforms(parse_source_metadata=True)

      True or self.response.out.write("done %r\n" % [
        attachment.filename, attachment.content_id,
        # dir(img),
      ],
      )
      True or self.response.out.write(
        json.dumps(img.get_original_metadata(), sort_keys=True, indent=4, separators=(',', ': '))
      )

    reverse_geocode_result = auth.googlemaps.reverse_geocode((40.714224, -73.961452))
    # self.response.out.write(json.dumps(reverse_geocode_result, sort_keys=True, indent=4, separators=(',', ': ')))

    address = None
    if len(reverse_geocode_result) > 0 and "formatted_address" in reverse_geocode_result[0]:
      address = reverse_geocode_result[0]["formatted_address"]
    # self.response.out.write("\n\nAddress: %r\n\n" % address)

    email = users.get_current_user().email()
    msg = mail.EmailMessage(
      sender=email,
      to=email,
      subject="new hello",
    )

    mime = MIMEMultipart('related')
    #  alternative = MIMEMultipart('alternative')
    #  mime.attach(alternative)
    #  alternative.attach(MIMEText("""some img""", 'plain', 'utf-8'))
    #  alternative.attach(MIMEText("""<img src="cid:foo">Hello World""",'html', 'utf-8'))
    mime.attach(MIMEText("""<img src="cid:foo">Hello World""",'html', 'utf-8'))

    image_data = attachment.payload.decode()
    img = images.Image(image_data=image_data)
    img.rotate(0)
    img.execute_transforms(parse_source_metadata=True)
    meta = img.get_original_metadata()
    orientaion = meta.get("Orientation", 1)
    if orientaion == 3:
      img.rotate(180)
      img.execute_transforms()

    text_img = Image.new('RGBA', (100,100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)
    draw.text((0, 0), 'HELLO TEXT jhfjhjdhsfhjdsfjhdfshjjdfshhjdfshjfdshjjhdfshjfds hjdf', font=ImageFont.load_default())

    draw.pieslice([0, 0, 100,100], 0, 90, "blue", "green")
    # draw.rectangle([(0,0), (200,200)], "blue", "green")
    text_img = text_img.rotate(135)
    draw = ImageDraw.Draw(text_img)
    draw.text((47, 20), '1', font=ImageFont.load_default())

    text_img = text_img.rotate(33)


    output = StringIO.StringIO()
    text_img.save(output, format="png")
    text_layer = output.getvalue()
    output.close()

    # TODO(ark) handle orientation == 3 (rotate 180 degrees)
    # http://www.impulseadventure.com/photo/exif-orientation.html

    merged = images.composite([(img, 0, 0, 1.0, images.TOP_LEFT),
                               (text_layer, 0, 0, 1.0, images.TOP_LEFT)],
                              640, 480)

    img_part = MIMEImage(merged, name="whut.png")
    img_part.add_header("Content-ID", "<foo>")

    mime.attach(img_part)

    msg.update_from_mime_message(mime)
    # msg.send()

    # self.response.out.write(mime.as_string())

    self.response.headers['Content-Type'] = 'image/png'
    self.response.write(merged)
