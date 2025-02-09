module.exports = {
    questions({inquirer, gitInfo}) {
      const ui = new inquirer.ui.BottomBar();
      ui.log.write(`============================`);
      ui.log.write(`Current Branch is ${gitInfo.branch}`);
      ui.log.write(`============================`);
      ui.log.write(``);
  
      return [
        {
          type: 'input',
          name: 'input1',
        },
        {
          type: 'input',
          name: 'input2',
        },
      ]
  
    },
    commitMessage({answers, gitInfo}) { 
        
    
      return `${answers.input1}\n${answers.input2}`
    }
  }