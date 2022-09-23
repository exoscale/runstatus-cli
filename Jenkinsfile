@Library('jenkins-pipeline') _

node {
  // Wipe the workspace so we are building completely clean
  cleanWs()

  withEnv(['PYTHON_EXECUTABLE=/usr/bin/python3']) {
    try {
      dir('src') {
        stage('checkout source code') {
          checkout scm
        }
        updateGithubCommitStatus('PENDING', "${env.WORKSPACE}/src")
        stage('test') {
          pythonLint()
        }
        stage('build') {
          gitPbuilder('xenial')
        }
      }
      stage('aptly upload') {
        aptlyBranchUpload('xenial', 'main', 'build-area/*deb')
      }
    }
    catch (err) {
      currentBuild.result = 'FAILURE'
      updateGithubCommitStatus('FAILURE', "${env.WORKSPACE}/src")
      throw err
    }
    finally {
      if (currentBuild.result != 'FAILURE') {
        updateGithubCommitStatus('SUCCESS', "${env.WORKSPACE}/src")
      }
      cleanWs cleanWhenFailure: false
    }
  }
}

def pythonLint() {
  docker.withRegistry("https://${EXOSCALE_DOCKER_REGISTRY}") {
    def python = docker.image("${EXOSCALE_DOCKER_REGISTRY}/exoscale/python:3.8-focal-build")
    python.pull()
    python.inside("-u root -v /home/exec/.cache:/root/.cache --net=host") {
      venv "pip install -U flake8 flake8-bugbear flake8-import-order"
      venv "flake8 rscli"
    }
  }
}
