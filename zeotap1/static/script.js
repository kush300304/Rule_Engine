function ruleEngine() {
    return {
        rules: [],
        newRule: {
            name: '',
            description: '',
            rule_string: ''
        },
        combinedRule: {
            name: '',
            description: '',
            rule_ids: []
        },
        evaluateRule: {
            rule_id: '',
            data: '',
            result: null
        },
        
        init() {
            this.fetchRules();
        },
        
        fetchRules() {
            fetch('/api/rules/')
                .then(response => response.json())
                .then(data => {
                    this.rules = data;
                })
                .catch(error => console.error('Error fetching rules:', error));
        },
        
        createRule() {
            fetch('/api/rules/create_rule/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.newRule)
            })
            .then(response => response.json())
            .then(data => {
                this.rules.push(data);
                this.newRule = { name: '', description: '', rule_string: '' };
                alert('Rule created successfully!');
            })
            .catch(error => console.error('Error creating rule:', error));
        },
        
        combineRules() {
            fetch('/api/rules/combine_rules/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.combinedRule)
            })
            .then(response => response.json())
            .then(data => {
                this.rules.push(data);
                this.combinedRule = { name: '', description: '', rule_ids: [] };
                alert('Rules combined successfully!');
            })
            .catch(error => console.error('Error combining rules:', error));
        },
        
        evaluateRuleFunction() {
            try {
                const parsedData = JSON.parse(this.evaluateRule.data);
                fetch('/api/rules/evaluate_rule/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        rule_id: this.evaluateRule.rule_id,
                        data: parsedData
                    })
                })
                .then(response => response.json())
                .then(data => {
                    this.evaluateRule.result = data.result;
                })
                .catch(error => console.error('Error evaluating rule:', error));
            } catch (e) {
                alert('Invalid JSON format in evaluation data');
            }
        },
        
        deleteRule(ruleId) {
            fetch(`/api/rules/${ruleId}/`, {
                method: 'DELETE'
            })
            .then(() => {
                this.rules = this.rules.filter(rule => rule.id !== ruleId);
                alert('Rule deleted successfully!');
            })
            .catch(error => console.error('Error deleting rule:', error));
        }
    }
}