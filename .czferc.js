module.exports = {
    questions: [
        {
            type: 'input',
            name: 'scope',
            message:
              'What is the scope of this change (e.g. component or file name): (press enter to skip)\n'
          },
          {
            type: 'input',
            name: 'issues',
            message: 'Add issue references (e.g. "fix #123", "re #123".):\n',
            when: answers => answers.isIssueAffected,
            default: undefined,
            validate: (issues) => issues.length === 0 ? 'issues is required' : true
          }
    ],
    commit({answers, gitInfo}) { 

    console.log(answers, gitInfo)
        
    const scope = answers.scope ? `(${answers.scope})` : '';
      return `OPTIMUSBOT-2: feat${answers.scope}\nSome extra information that helps to clarify the commit message.`
    }
  }