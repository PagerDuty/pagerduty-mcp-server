def BRANCH_ACTUAL = env.CHANGE_BRANCH ? env.CHANGE_BRANCH : env.BRANCH_NAME
pipeline {
    agent {
        node {
            label 'ec2-fleet'
            customWorkspace "/tmp/workspace/${BUILD_TAG}"
        }
    }

    options {
        timeout time: 1, unit: 'HOURS'
        timestamps()
        ansiColor 'xterm'
    }

    environment {
        GITHUB_TOKEN = credentials('github-api-token')
        GITHUB_PACKAGES_TOKEN = credentials('github-api-token')
        LAST_COMMITTER = sh(script: 'git log -1 --format=%ae', returnStdout: true).trim()
    }

    parameters {
        booleanParam(name: 'CLEAN', defaultValue: false, description: "Run 'make clean' before building")
    }

    stages {
        stage('Setup') {
            steps {
                sh "git checkout ${BRANCH_ACTUAL}"
                configFileProvider([configFile(fileId: 'git-askpass', variable: 'GIT_ASKPASS')]) {
                    sh 'chmod +x \$GIT_ASKPASS'
                    sh 'make setup'
                }
            }
        }
        stage('Lint') {
            steps {
                sh 'make -j4 lint'
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'make test'
            }
        }

        stage('Version') {
            when {
                not {
                    environment name: 'LAST_COMMITTER', value: 'bot@logdna.com'
                }
            }
            steps {
                sh 'make version'
            }
        }

        stage('Build') {
            when {
                anyOf {
                    environment name: 'LAST_COMMITTER', value: 'bot@logdna.com'
                    not { anyOf {
                            branch 'main'
                            branch 'master'
                    } }
                }
            }
            steps {
                sh 'make build'
                archiveArtifacts allowEmptyArchive: true, artifacts: 'tmp/version-info', caseSensitive: false, followSymlinks: false
            }
        }

        stage('Publish') {
            when {
                allOf {
                    environment name: 'LAST_COMMITTER', value: 'bot@logdna.com'
                    anyOf {
                        branch 'master'
                        branch 'main'
                    }
                }
            }

            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws',
                    accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                    secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                ]]) {
                    sh 'make publish'
                }
            }
        }
    }
    post {
        always {
            // Generate JUnit, PEP8, Pylint and Coverage reports.
            withChecks('Unit Tests') {
                junit 'reports/*junit.xml'
            }
            publishCoverage adapters: [coberturaAdapter(path: 'reports/coverage.xml')]
        }
    }
}
