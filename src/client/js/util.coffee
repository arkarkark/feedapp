# from: http://stackoverflow.com/questions/6659351/removing-all-script-tags...
# crude attempt to sanitize some html for display on my site
# TODO(ark) use angulars $sce module?

stripScripts = (s) ->
  div = document.createElement('div')
  div.innerHTML = s
  scripts = div.getElementsByTagName('script')
  i = scripts.length
  while i--
    scripts[i].parentNode.removeChild scripts[i]
  div.innerHTML
