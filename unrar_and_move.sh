#/bin/bash

# This script will scan the $TORRENTDIR for newly completed torrents.
# Upon completion, all non-sample media files, (mkv, avi, mp4, etc.)
# which have not already been copied, will be copied to the $VIDEODIR.
# If no media files are found, then a rar file will be located and if
# the existing media file has not already been, it will be extracted
# into the $VIDEODIR.
#
# If the torrent which is downloaded is not a media file, it will be
# ignored (for now).

#TIME=$(/bin/date +%Y%m%d_%H%M%S)
MV=/usr/bin/mv
LS=/usr/bin/ls
RM=/usr/bin/rm
FIND=/usr/bin/find
GREP=/usr/bin/grep
RSYNC="/usr/bin/rsync"
UNRAR=/usr/bin/unrar

TORRENTDIR=/home/herlo/Torrents
VIDEODIR=/home/herlo/Videos
AUDIODIR=/home/herlo/Music
EXCLUDEFILE=${TORRENTDIR}/.unrar_excludes

FORCE=0
MEDIATYPES=(avi mp4 mkv)
AUDIOTYPES=(mp3 ogg aac)


copy_video_files () {
  for mt in ${MEDIATYPES[*]}; do
#    echo "MT: ${mt}"
#    echo "$1" | ${GREP} ${mt} #&> /dev/null
    if [ $? -eq 0 ]; then
      if [ ! -f "${VIDEODIR}/$1" ] || [ ${FORCE} -eq 1 ]; then
        echo "COPYING VIDEO FILE: $1"
        /usr/bin/rsync -a "${1}" ${VIDEODIR}
        break
#      else
#        ${RM} -f $1
#        break
      fi
    fi
  done
}

copy_audio_files () {
  for mt in ${AUDIOTYPES[*]}; do
    if [ $? -eq 0 ]; then
      if [ ! -f "${AUDIODIR}/$1" ] || [ ${FORCE} -eq 1 ]; then
        /usr/bin/rsync -a "${1}" ${AUDIODIR}
        break
#      else
#        ${RM} -f $1
#        break
      fi
    fi
  done
}

copy_video_dirs () {
  pushd "${1}" &> /dev/null

  SAVEIFS=${IFS}
  IFS=$(echo -en "\n\b")

  for mt in ${MEDIATYPES[*]}; do
#    FILES="$(${LS} -1 *.${mt} 2> /dev/null)"
#    echo "FILES: ${FILES}"
    FILES="$(${FIND} . -mindepth 1 -maxdepth 1 -not -iname '*sample*' -iname "*.${mt}" 2> /dev/null)"
    if [ -n "${FILES}" ]; then
      SAVEIFS=${IFS}
      IFS=$'\n'
      for f in *.${mt}; do
        EXCLUDED=$(${GREP} -i "${f}" "${EXCLUDEFILE}")
        if [ -n "$EXCLUDED" ]; then
          continue
        fi
        IFS=${SAVEIFS}
        if [ ! -e "${VIDEODIR}/${f}" ] || [ ${FORCE} -eq 1 ]; then
          echo /usr/bin/rsync -a "${f}" ${VIDEODIR} &> /dev/null
        fi
      done
      IFS=${SAVEIFS}
    fi
  done
  popd &> /dev/null
  IFS=${SAVEIFS}
}

copy_audio_dirs () {
  pushd "${1}" &> /dev/null
  for mt in ${AUDIOTYPES[*]}; do
#    FILES="$(${LS} -1 *.${mt} 2> /dev/null)"
    FILES="$(${FIND} . -mindepth 1 -maxdepth 1 -not -iname '*sample*' -iname "*.${mt}" 2> /dev/null)"
    if [ -n "${FILES}" ]; then
      if [ ! -d "${AUDIODIR}/${1}" ]; then
        mkdir -p "${AUDIODIR}/${1}"
      fi
      SAVEIFS=${IFS}
      IFS=$'\n'
      for f in *.${mt}; do
        IFS=${SAVEIFS}
        if [ ! -e "${AUDIODIR}/${1}/${f}" ] || [ ${FORCE} -eq 1 ]; then
          /usr/bin/rsync -a "${f}" "${AUDIODIR}/${1}/" # &> /dev/null
        fi
      done
      IFS=${SAVEIFS}
    fi
  done
  popd &> /dev/null
}

extract_media_dirs () {
  pushd "$1" &> /dev/null
  for f in *.rar; do
    MEDIAFILE=$(${UNRAR} lb "${f}")
    EXCLUDED=$(${GREP} -i "${MEDIAFILE}" "${EXCLUDEFILE}")
    if [ -n "$EXCLUDED" ]; then
      continue
    fi
    if [ ! -e "${VIDEODIR}/${MEDIAFILE}" ] || [ ${FORCE} -eq 1 ]; then
      echo "EXTRACTING: ${MEDIAFILE}"
      ${UNRAR} -idq -y e "${f}"
      /usr/bin/rsync -a "${MEDIAFILE}" ${VIDEODIR} &> /dev/null
    fi
  done
  popd &> /dev/null
}

pushd ${TORRENTDIR} &> /dev/null

for file in *; do

  EXCLUDED=$(${GREP} -i "${file}" "${EXCLUDEFILE}")
  if [ -n "$EXCLUDED" ]; then
    continue
  fi
  #echo "${file}: ${EXCLUDED}"

  if [ "${EXCLUDED}" == "0" ]; then
    echo "FILE: ${1} being excluded"
    continue
  fi

  #echo "${file}" #&> /dev/null
  if [ -d "${file}" ]; then
    copy_video_dirs "${file}"
    copy_audio_dirs "${file}"
    extract_media_dirs "${file}"
  elif [ -f "${file}" ]; then
    copy_video_files "${file}"
    copy_audio_files "${file}"
  fi

done

popd &> /dev/null

