/**
 * Sample JavaScript code with undocumented functions and classes for testing DocuAI.
 */

function calculateSum(numbers) {
    return numbers.reduce((sum, num) => sum + num, 0);
}

function filterActiveUsers(users) {
    return users.filter(user => user.active === true);
}

function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', options);
}

class Calculator {
    constructor() {
        this.history = [];
    }
    
    add(a, b) {
        const result = a + b;
        this.history.push(`${a} + ${b} = ${result}`);
        return result;
    }
    
    subtract(a, b) {
        const result = a - b;
        this.history.push(`${a} - ${b} = ${result}`);
        return result;
    }
    
    getHistory() {
        return this.history;
    }
}

class UserService {
    constructor(apiClient) {
        this.api = apiClient;
        this.cache = new Map();
    }
    
    async getUser(id) {
        if (this.cache.has(id)) {
            return this.cache.get(id);
        }
        
        const user = await this.api.fetchUser(id);
        this.cache.set(id, user);
        return user;
    }
    
    async updateUser(id, userData) {
        const updatedUser = await this.api.updateUser(id, userData);
        this.cache.set(id, updatedUser);
        return updatedUser;
    }
}
