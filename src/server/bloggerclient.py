from googleapiclient.discovery import build
# from googleapiclient import errors

class BloggerClient(object):
  def __init__(self, decorator):
    """Creates the Blogger client connection"""
    decorated_http = decorator.http()
    self.service = build('blogger', 'v3', http=decorated_http)
    self.decorator = decorator

  def blogsListByUser(self, userId="self", status=None, fetchUserInfo=None, role=None, view=None):
      decorated_http = self.decorator.http()
      blogs = self.service.blogs()
      request = blogs.listByUser(
        userId=userId,
        status=status,
        fetchUserInfo=fetchUserInfo,
        role=role,
        view=view)
      return request.execute(decorated_http)
