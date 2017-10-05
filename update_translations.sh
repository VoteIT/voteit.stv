 #!/bin/bash
 #You need lingua and gettext installed to run this
 
 echo "Updating voteit.stv.pot"
 pot-create -d voteit.stv -o voteit/stv/locale/voteit.stv.pot .
 echo "Merging Swedish localisation"
 msgmerge --update voteit/stv/locale/sv/LC_MESSAGES/voteit.stv.po voteit/stv/locale/voteit.stv.pot
 echo "Updated locale files"
 