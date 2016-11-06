m = angular.module "mailServices"

m.factory "MailFeed", ($resource) ->
  $resource "/data/mail/feed.json?id=:id", { id: "@id" }, {}

m.factory "MailFeedItem", ($resource) ->
  $resource(
    "/data/mail/item.json?id=:id&parent_id=:parent_id&action=:action"
    {
      id: "@id"
      parent_id: "@parent_id"
    }
    {
      tombstone:
        method: "POST"
        params: action: "tombstone"
    }
  )
