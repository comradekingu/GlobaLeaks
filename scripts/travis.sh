#!/bin/bash

set -e

if [ -z "$GLREQUIREMENTS" ]; then
  GLREQUIREMENTS="trusty"
fi

setupClientDependencies() {
  cd $TRAVIS_BUILD_DIR/client  # to install frontend dependencies
  npm install -g grunt grunt-cli bower
  npm install -d
  bower update
  ./node_modules/protractor/bin/webdriver-manager update
  if [ "$1" = 1 ]; then
    grunt build
  fi
}

setupBackendDependencies() {
  cd $TRAVIS_BUILD_DIR/backend  # to install backend dependencies
  rm -rf requirements.txt
  ln -s requirements/requirements-${GLREQUIREMENTS}.txt requirements.txt
  pip install -r requirements.txt
  pip install coverage coveralls
}

setupDependencies() {
  setupClientDependencies $1
  setupBackendDependencies
}

if [ "$GLTEST" = "test" ]; then

  echo "Running backend unit tests"
  setupDependencies
  cd $TRAVIS_BUILD_DIR/backend
  coverage run setup.py test

  echo "Running API tests"
  $TRAVIS_BUILD_DIR/backend/bin/globaleaks -z travis --disable-mail-notification
  sleep 3
  cd $TRAVIS_BUILD_DIR/client
  grunt mochaTest

  if [ "$GLREQUIREMENTS" = "trusty" ]; then
    echo "Running BrowserTesting locally collecting code coverage"
    cd $TRAVIS_BUILD_DIR/client

    grunt end2end-coverage-instrument

    $TRAVIS_BUILD_DIR/backend/bin/globaleaks -z travis -c -k9 --disable-mail-notification
    sleep 3

    cd $TRAVIS_BUILD_DIR/client
    grunt end2end-coverage-run

    cd $TRAVIS_BUILD_DIR/backend
    coveralls --merge=../client/coverage/coveralls.json || true
  fi

elif [ "$GLTEST" = "lint" ]; then

  setupDependencies
  echo "Running lint checks"
  cd $TRAVIS_BUILD_DIR/client
  grunt eslint

elif [ "$GLTEST" = "build_and_install" ]; then

  echo "Running Build & Install and BrowserTesting tests"
  # we build all packages to test build for each distributions and then we test against trusty
  sudo apt-get update -y
  sudo apt-get install -y debhelper devscripts dh-apparmor dh-python python python-pip python-setuptools python-sphinx
  curl -sL https://deb.nodesource.com/setup | sudo bash -
  sudo apt-get install -y nodejs
  cd $TRAVIS_BUILD_DIR
  ./scripts/build.sh -d all -t $TRAVIS_COMMIT -n
  sudo mkdir -p /data/globaleaks/deb/
  sudo cp GLRelease-trusty/globaleaks*deb /data/globaleaks/deb/
  set +e # avoid to fail in case of errors cause apparmor will always cause the failure
  sudo ./scripts/install.sh
  set -e # re-enable to fail in case of errors
  sudo sh -c 'echo "NETWORK_SANDBOXING=0" >> /etc/default/globaleaks'
  sudo sh -c 'echo "APPARMOR_SANDBOXING=0" >> /etc/default/globaleaks'
  sudo /etc/init.d/globaleaks restart
  sleep 3
  setupClientDependencies
  cd $TRAVIS_BUILD_DIR/client
  grunt protractor:test

elif [[ $GLTEST =~ ^end2end-.* ]]; then

  echo "Running Browsertesting on Saucelabs"

  declare -a capabilities=(
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Internet Explorer\", \"version\":\"9\", \"platform\":\"Windows 7\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Internet Explorer\", \"version\":\"10\", \"platform\":\"Windows 8\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Internet Explorer\", \"version\":\"11\", \"platform\":\"Windows 10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Firefox\", \"version\":\"34\", \"platform\":\"Linux\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Firefox\", \"version\":\"45\", \"platform\":\"Linux\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Firefox\", \"version\":\"beta\", \"platform\":\"Windows 10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Chrome\", \"version\":\"37\", \"platform\":\"Linux\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Chrome\", \"version\":\"48\", \"platform\":\"Linux\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Chrome\", \"version\":\"beta\", \"platform\":\"Windows 10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Safari\", \"version\":\"8\", \"platform\":\"OS X 10.10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Safari\", \"version\":\"9\", \"platform\":\"OS X 10.11\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Android\", \"version\": \"4.4\", \"deviceName\": \"Android Emulator\", \"deviceOrientation\": \"portrait\", \"deviceType\": \"tablet\", \"platform\": \"Linux\"}'."
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\":\"Android\", \"version\": \"5.1\", \"deviceName\": \"Android Emulator\", \"deviceOrientation\": \"portrait\", \"deviceType\": \"tablet\", \"platform\": \"Linux\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\": \"iPhone\", \"version\": \"7.1\", \"deviceName\": \"iPad Simulator\", \"deviceOrientation\": \"portrait\", \"platform\":\"OS X 10.10\"}'"
    "export SELENIUM_BROWSER_CAPABILITIES='{\"browserName\": \"iPhone\", \"version\": \"9.2\", \"deviceName\": \"iPad Simulator\", \"deviceOrientation\": \"portrait\", \"platform\":\"OS X 10.10\"}'"
  )

  testkey=$(echo $GLTEST | cut -f2 -d-)

  ## now loop through the above array
  capability=${capabilities[${testkey}]}

  echo "Testing Configuration: ${testkey}"
  setupDependencies 1
  eval $capability
  $TRAVIS_BUILD_DIR/backend/bin/globaleaks -z travis --port 9000 --disable-mail-torification
  sleep 3
  cd $TRAVIS_BUILD_DIR/client
  grunt protractor:saucelabs

fi
