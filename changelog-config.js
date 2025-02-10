// changelog-config.js
module.exports = {
    parserOpts: {
      // This regex does the following:
      // - Optionally captures a Jira ticket (e.g., OPTIMUSBOT-1234) at the start followed by whitespace.
      // - Then captures one of the conventional commit types.
      // - Optionally captures a scope wrapped in parentheses.
      // - Finally, captures the subject after a colon and space.
      headerPattern: /^(?:([A-Z]+-\d+)\s+)?(feat|fix|docs|style|refactor|perf|test|chore)(?:\(([^)]+)\))?: (.*)$/,
      // Maps regex capture groups to their semantic names:
      // Group 1: jira, Group 2: type, Group 3: scope, Group 4: subject
      headerCorrespondence: ['jira', 'type', 'scope', 'subject']
    },
    // You can optionally define writer options here (e.g., for grouping, formatting, etc.)
    writerOpts: {
      // Example: how to display commit types in the changelog
      transform: (commit, context) => {
        // Remove the jira property if you don't want it in the changelog output.
        delete commit.jira;
        // Optionally, adjust commit.subject, etc.
        return commit;
      }
    }
  };
  