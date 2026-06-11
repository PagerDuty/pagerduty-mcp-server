# Contributing to PagerDuty MCP Server

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## **Did you find a bug?**

* **Do not open up a GitHub issue if the bug is a security vulnerability**, and instead send us an [email](mailto:open-source@pagerduty.com).

* **Ensure the bug was not already reported** by searching on GitHub's [issues](https://github.com/pagerduty/pagerduty-mcp-server/issues) page.

* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/pagerduty/pagerduty-mcp-server/issues/new?labels=bug&projects=&template=bug_report.md). **Use the bug template.**

## **Do you intend to add a new feature or change an existing one?**

* Check for a similar feature request on the [issues](https://github.com/pagerduty/pagerduty-mcp-server/issues) page.
  
* If you can't find it, open an issue on GitHub using the [Feature Request](https://github.com/pagerduty/pagerduty-mcp-server/issues/new?assignees=&labels=enhancement&projects=&template=feature_request.md&title=) template.

* Provide as much details as possible so the request can be analysed by the team.

* If you aren't sure about the feature you are about to request reach out to other community members on [PagerDuty Community Forum](https://community.pagerduty.com).

> Note: Features will be reviewed by the core team and discussed with the contributor. Different factors may cause features to be rejected or postponed.

## Pull Requests

Contributions via pull requests are much appreciated but we need you to follow some basic rules so we can work more effectively.

### Step 1: Find something to work on

If you want to contribute a specific feature or fix you have in mind, look at active [pull requests](https://github.com/pagerduty/pagerduty-mcp-server/pulls) to see if someone else is already working on it. If not, please propose that feature request/fix on the [issues page](https://github.com/pagerduty/pagerduty-mcp-server/issues). You will need to reference the issue number on the PR.

On the other hand, if you are here looking for an issue/bug to work on, check out our [backlog of issues](https://github.com/pagerduty/pagerduty-mcp-server/issues) and find something that looks interesting. We label our issues with [GitHub's default labels](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels#about-default-labels). Use that as a reference.

It's a good idea to keep the priority of issues in mind when deciding what to work on. If we have labelled an issue as `low priority`, it means it's something we won't get to work soon while `high priority` issues have a bigger impact, so we are much more likely to give a PR for those issues prompt attention.

### Step 2: Design

We ask you to seek feedback and consensus on your proposed change by iterating on a design document. This is especially useful when you plan a big change or feature, or you want advice on what would be the best path forward.

If you're picking up an existing issue, you can simply post your comment and discuss your proposed changes. If instead you're proposing a new feature, you can start by creating a new [feature request issue](https://github.com/pagerduty/pagerduty-mcp-server/issues/new?assignees=&labels=enhancement&projects=&template=feature_request.md&title=) and discuss your proposed change with the maintainers.

Another way to collect feedback on a new feature request is by sharing it in [PagerDuty's community forum](https://community.pagerduty.com).

### Step 3: Have fun coding!

Do your thing but please make sure you follow the rules:

* Work against the latest source on the **next** branch. This will allow maintainers to publish pre-release versions with changes before releasing a stable version.
* Try to maintain a single feature/bugfix per pull request. It's okay to introduce a little bit of housekeeping changes along the way, but try to avoid conflating multiple features. Eventually, all these are going to go into a single commit, so you can use that to frame your scope.
* Add **unit tests** that test your changes when applicable. This is especially important for new features and bug fixes, as it helps you to make sure that your changes are working as intended.
* Lint and test the code. Pull request builds will run the same checks as well.
* Follow conventional commits guidelines.

    >**Note:** Maintainers use a [Visual Studio Code extension](https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits) to simplify the enforcement of [conventional commits](https://www.conventionalcommits.org).
    >
    > There is also a pre-commit hook configured to prevent not doing so.

### Step 4: Run Evals

When making changes to an MCP server, it's critical to ensure that the tools and their descriptions are suitable for the expected use cases. To run a set of test questions against the modified MCP server run:

```
python tests/evals/run_tests.py
```

### Step 5: Pull Request

Once you're done with your changes, you can open a pull request. Make sure to follow the checklist inside the pull request template.

Create a commit with your changes and push them to a new branch/fork then create a [pull request on GitHub](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).
  
  > **Note:** Core members can push directly to a branch on the repo (following the same conventions detailed below).

Pull request title and message (and PR title and description) must adhere to [conventional commits](https://www.conventionalcommits.org), this is enforced by the CI. This is a summary of the rules:

* The title must begin with `feat: title`, `fix: title`, `refactor: title` or `chore: title`, etc.
* Title should be lowercase.
* No period at the end of the title.

The pull request body should describe _motivation_ and follow the template provided as closely as possible. Think about your code reviewers and what information they need in order to understand what you did. If it's a big commit (hopefully not), try to provide some good entry points so it will be easier to follow.

The body should also include a reference to the issue that this PR is related to in the appropriate section.

Once the pull request is submitted, a reviewer will be assigned by the maintainers.

Discuss review comments and iterate until you get at least one "Approve". When iterating, push new commits to the same branch. Usually, all these are going to be squashed when the maintainers merge to `next` and finally to `main`. The commit messages should be hints for you when you finalize your merge commit message.


### Step 6: Merge

Once approved and tested, one of the maintainers will squash-merge to `next` and finally `main` and will use your PR title/description as the commit message. Your name will be also added to the Release Notes of the next release.

## Thank you!

PagerDuty MCP Server is an open source project and therefore needs the community to support it. We encourage you to help us out!

Thanks! 💚