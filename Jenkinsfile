@Library('jenkins-pipeline') _

node {
  // Wipe the workspace so we are building completely clean
  cleanWs()

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

def pythonLint() {
  docker.withRegistry('https://registry.internal.exoscale.ch') {
    def python = docker.image('registry.internal.exoscale.ch/exoscale/python:latest')
    python.pull()
    python.inside("-u root -v /home/exec/.cache:/root/.cache --net=host") {
      withPythonEnv('python') {
        pythonLint('rscli')
      }
    }
  }
}
