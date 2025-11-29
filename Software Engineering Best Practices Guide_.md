

# **Definitive Guide to Modern Software Engineering Best Practices**

This document establishes the foundational software engineering principles and best practices for our team. Adherence to these guidelines is essential for building high-quality, maintainable, secure, and scalable software. This guide is a living document, intended to codify our collective expertise and serve as a single source of truth for all development activities.

## **1\. Architectural & Design Principles**

This section covers the high-level, language-agnostic principles that guide the structure and design of our software. These principles are fundamental to creating systems that are easy to maintain, extend, and reason about over time. They help us manage complexity and reduce the cost of change.

### **1.1. The SOLID Principles**

The SOLID principles, introduced by Robert C. Martin, are five foundational principles of object-oriented design that, when applied together, make it more likely that a programmer will create a system that is easy to maintain and extend over time. They are cornerstones of building robust and scalable applications.

While each of the five SOLID principles addresses a specific design aspect, they collectively contribute to a single overarching goal: effective dependency management. SRP isolates change by ensuring a class has only one axis of change. OCP uses abstraction to allow extension without modifying existing code, thus managing dependencies on concrete implementations. LSP ensures that dependencies on a base type are safe. ISP prevents clients from depending on methods they don't use. DIP explicitly inverts the direction of dependencies from concrete details to abstractions. The primary benefit of a SOLID architecture is resilience to change. When dependencies are managed correctly, a modification in one part of the system (a "detail") does not cascade into unrelated parts of the system (the "high-level policy"). This directly translates to lower maintenance costs and higher development velocity.

#### **1.1.1. Single Responsibility Principle (SRP)**

A class should have only one reason to change, meaning it should have only one job or responsibility.1 When a class handles multiple concerns (e.g., business logic, data persistence, and presentation), a change in one of those concerns forces a change in the class, increasing the risk of introducing bugs into the other, unrelated concerns.4 This principle is about grouping related features together so they change for the same reason, and separating features that change for different reasons.4

##### **Bad Example (Python)**

The following FileManager class violates SRP because it has two distinct responsibilities: reading and writing file content, and compressing/decompressing ZIP archives. A change in the file I/O logic or a change in the compression logic would both require modifying this single class.

Python

\# Bad: This class has two responsibilities  
from pathlib import Path  
from zipfile import ZipFile

class FileManager:  
    def \_\_init\_\_(self, filename):  
        self.path \= Path(filename)

    def read(self, encoding="utf-8"):  
        return self.path.read\_text(encoding)

    def write(self, data, encoding="utf-8"):  
        self.path.write\_text(data, encoding)

    def compress(self):  
        with ZipFile(self.path.with\_suffix(".zip"), mode="w") as archive:  
            archive.write(self.path)

    def decompress(self):  
        with ZipFile(self.path.with\_suffix(".zip"), mode="r") as archive:  
            archive.extractall()

##### **Good Example (Python)**

The responsibilities are separated into two distinct classes, FileManager and ZipFileManager. Each class now has a single responsibility, making them more modular, easier to test, and simpler to maintain.5

Python

\# Good: Responsibilities are separated into two classes  
from pathlib import Path  
from zipfile import ZipFile

class FileManager:  
    def \_\_init\_\_(self, filename):  
        self.path \= Path(filename)

    def read(self, encoding="utf-8"):  
        return self.path.read\_text(encoding)

    def write(self, data, encoding="utf-8"):  
        self.path.write\_text(data, encoding)

class ZipFileManager:  
    def \_\_init\_\_(self, filename):  
        self.path \= Path(filename)

    def compress(self):  
        with ZipFile(self.path.with\_suffix(".zip"), mode="w") as archive:  
            archive.write(self.path)

    def decompress(self):  
        with ZipFile(self.path.with\_suffix(".zip"), mode="r") as archive:  
            archive.extractall()

##### **Bad Example (TypeScript)**

The Student class below violates SRP by handling three different responsibilities: account management, grade calculation, and data reporting. A change request related to any of these areas would force a modification to the Student class.3

TypeScript

// Bad: This class has three responsibilities  
class Student {  
    public createStudentAccount() {  
        // Logic to create a student account in the database  
    }

    public calculateStudentGrade() {  
        // Logic to calculate the student's current grade  
    }

    public generateStudentReport() {  
        // Logic to generate and format a report card  
    }  
}

##### **Good Example (TypeScript)**

The single Student class is broken down into three smaller classes, each with a single, well-defined responsibility. This separation of concerns makes the system more robust and easier to manage.3

TypeScript

// Good: Each class has a single responsibility  
class StudentAccount {  
    public createStudentAccount() {  
        // Logic to create a student account in the database  
    }  
}

class StudentGradeCalculator {  
    public calculateStudentGrade() {  
        // Logic to calculate the student's current grade  
    }  
}

class StudentReportGenerator {  
    public generateStudentReport() {  
        // Logic to generate and format a report card  
    }  
}

#### **1.1.2. Open/Closed Principle (OCP)**

Software entities (classes, modules, functions) should be open for extension but closed for modification.1 This means you should be able to add new functionality without changing existing, tested code. This is typically achieved by relying on abstractions (like interfaces or abstract base classes) and using techniques like dependency injection or inheritance.

##### **Bad Example (Python)**

The AreaCalculator class violates OCP. To add a new shape, such as a Triangle, one must modify the sum method by adding another elif block. This makes the class brittle and requires re-testing the existing logic every time a new shape is introduced.

Python

\# Bad: This class must be modified to support new shapes  
import math

class Square:  
    def \_\_init\_\_(self, length):  
        self.length \= length

class Circle:  
    def \_\_init\_\_(self, radius):  
        self.radius \= radius

class AreaCalculator:  
    def \_\_init\_\_(self, shapes):  
        self.shapes \= shapes

    def sum(self):  
        total\_area \= 0  
        for shape in self.shapes:  
            if isinstance(shape, Square):  
                total\_area \+= shape.length \*\* 2  
            elif isinstance(shape, Circle):  
                total\_area \+= math.pi \* shape.radius \*\* 2  
        return total\_area

##### **Good Example (Python)**

An abstract base class Shape is introduced with an abstract area method. Each concrete shape class inherits from Shape and provides its own implementation of area. The AreaCalculator now works with the Shape abstraction and no longer needs to know about concrete shape types. It is now open to extension (new Shape subclasses can be added) but closed for modification.5

Python

\# Good: This class is open to extension, closed for modification  
import math  
from abc import ABC, abstractmethod

class Shape(ABC):  
    @abstractmethod  
    def area(self):  
        pass

class Square(Shape):  
    def \_\_init\_\_(self, length):  
        self.length \= length

    def area(self):  
        return self.length \*\* 2

class Circle(Shape):  
    def \_\_init\_\_(self, radius):  
        self.radius \= radius

    def area(self):  
        return math.pi \* self.radius \*\* 2

class AreaCalculator:  
    def \_\_init\_\_(self, shapes):  
        self.shapes \= shapes

    def sum(self):  
        total\_area \= 0  
        for shape in self.shapes:  
            total\_area \+= shape.area() \# Works with any object that conforms to the Shape interface  
        return total\_area

##### **Bad Example (TypeScript)**

The NotificationService must be modified to add SMS functionality. This change requires altering the constructor and the sendNotification method, which could break existing code that relies on the original class structure and method signature.6

TypeScript

// Bad: The class is modified to add new functionality  
class EmailService {  
    public sendEmail(email: string, message: string): void {  
        console.log(\`Email sent: ${message} to ${email}\`);  
    }  
}

class SMSService {  
    public sendSms(phone: number, message: string): void {  
        console.log(\`SMS sent: ${message} to ${phone}\`);  
    }  
}

class NotificationService {  
    private \_emailService: EmailService;  
    private \_smsService: SMSService; // Added for SMS

    constructor() {  
        this.\_emailService \= new EmailService();  
        this.\_smsService \= new SMSService(); // Modified constructor  
    }

    // Modified method signature and logic  
    public sendNotification(email: string, phone: number, message: string) {  
        this.\_emailService.sendEmail(email, message);  
        this.\_smsService.sendSms(phone, message);  
    }  
}

##### **Good Example (TypeScript)**

Instead of modifying the original NotificationService, a new OrderNotificationService is created that *extends* it. This new class adds the SMS functionality without altering the existing, potentially widely-used base class. The original code remains untouched and stable, adhering to OCP.6

TypeScript

// Good: The class is extended to add new functionality  
class EmailService {  
    public sendEmail(email: string, message: string): void {  
        console.log(\`Email sent: ${message} to ${email}\`);  
    }  
}

class SMSService {  
    public sendSms(phone: number, message: string): void {  
        console.log(\`SMS sent: ${message} to ${phone}\`);  
    }  
}

class NotificationService {  
    private \_emailService: EmailService;

    constructor() {  
        this.\_emailService \= new EmailService();  
    }

    public sendEmailNotification(email: string, message: string) {  
        this.\_emailService.sendEmail(email, message);  
    }  
}

// Extend the original service to add new functionality  
class OrderNotificationService extends NotificationService {  
    private \_smsService: SMSService;

    constructor() {  
        super();  
        this.\_smsService \= new SMSService();  
    }

    public sendFullNotification(email: string, phone: number, message: string) {  
        this.sendEmailNotification(email, message); // Reuse parent functionality  
        this.\_smsService.sendSms(phone, message);  
    }  
}

#### **1.1.3. Liskov Substitution Principle (LSP)**

Subtypes must be substitutable for their base types without altering the correctness of the program.3 If a function is designed to work with a base type, it must be able to work with any subtype of that base type without any special handling or knowledge of the subtype. Violations often occur when a subclass changes a fundamental behavior or invariant of the parent class in an unexpected way. A common "code smell" for LSP violations is runtime type checking (e.g.,

instanceof), where code changes its behavior based on the specific subclass it receives.4

##### **Bad Example (Python)**

A Square is a type of Rectangle, so inheriting Square from Rectangle seems logical. However, this implementation violates LSP. A consumer of a Rectangle object expects to be able to set width and height independently. The Square subclass breaks this expectation (invariant) by linking the two properties. A function that receives a Rectangle and sets its width and height would produce unexpected results if passed a Square.5

Python

\# Bad: Square is not a valid substitute for Rectangle  
class Rectangle:  
    def \_\_init\_\_(self, width, height):  
        self.\_width \= width  
        self.\_height \= height

    def set\_width(self, width):  
        self.\_width \= width

    def set\_height(self, height):  
        self.\_height \= height

    def get\_area(self):  
        return self.\_width \* self.\_height

class Square(Rectangle):  
    def \_\_init\_\_(self, side):  
        super().\_\_init\_\_(side, side)

    def set\_width(self, width):  
        self.\_width \= width  
        self.\_height \= width

    def set\_height(self, height):  
        self.\_width \= height  
        self.\_height \= height

\# Client code that breaks the assumption  
def use\_rectangle(rect: Rectangle):  
    rect.set\_width(5)  
    rect.set\_height(4)  
    \# This assertion will fail if a Square is passed in, as area will be 16, not 20\.  
    assert rect.get\_area() \== 20

##### **Good Example (Python)**

The solution is to model the relationship differently. A generic Shape abstract base class is created, and both Rectangle and Square inherit from it as siblings. Now, any function that works with a Shape can safely use either a Rectangle or a Square without breaking, as there are no incorrect assumptions about their behavior.5

Python

\# Good: A shared abstraction allows for substitutability  
from abc import ABC, abstractmethod

class Shape(ABC):  
    @abstractmethod  
    def get\_area(self):  
        pass

class Rectangle(Shape):  
    def \_\_init\_\_(self, width, height):  
        self.width \= width  
        self.height \= height

    def get\_area(self):  
        return self.width \* self.height

class Square(Shape):  
    def \_\_init\_\_(self, side):  
        self.side \= side

    def get\_area(self):  
        return self.side \*\* 2

##### **Bad Example (TypeScript)**

This example mirrors the Python violation. The Square class extends Rectangle but changes the behavior of the setters. A function expecting a Rectangle would not work correctly if a Square instance were passed to it, as setting the height would unexpectedly change the width.3

TypeScript

// Bad: Square alters the core behavior of Rectangle's setters  
class Rectangle {  
    protected width: number \= 0;  
    protected height: number \= 0;

    public setWidth(width: number): void {  
        this.width \= width;  
    }

    public setHeight(height: number): void {  
        this.height \= height;  
    }

    public getArea(): number {  
        return this.width \* this.height;  
    }  
}

class Square extends Rectangle {  
    public setWidth(width: number): void {  
        this.width \= width;  
        this.height \= width;  
    }

    public setHeight(height: number): void {  
        this.width \= height;  
        this.height \= height;  
    }  
}

function testArea(shape: Rectangle) {  
    shape.setWidth(5);  
    shape.setHeight(10);  
    const area \= shape.getArea();  
    console.log(\`Expected area 50, got ${area}\`); // Will log "Expected area 50, got 100" for a Square  
}

const rect \= new Rectangle();  
const sq \= new Square();  
testArea(rect);  
testArea(sq);

##### **Good Example (TypeScript)**

By introducing a Shape interface, both Rectangle and Square can implement it independently. This removes the problematic inheritance relationship. A function can now safely operate on any object that conforms to the Shape interface, respecting the Liskov Substitution Principle.

TypeScript

// Good: A common interface ensures substitutability without breaking behavior  
interface Shape {  
    getArea(): number;  
}

class Rectangle implements Shape {  
    private width: number;  
    private height: number;

    constructor(width: number, height: number) {  
        this.width \= width;  
        this.height \= height;  
    }

    public getArea(): number {  
        return this.width \* this.height;  
    }  
}

class Square implements Shape {  
    private side: number;

    constructor(side: number) {  
        this.side \= side;  
    }

    public getArea(): number {  
        return this.side \* this.side;  
    }  
}

#### **1.1.4. Interface Segregation Principle (ISP)**

Clients should not be forced to depend on interfaces they do not use.3 Instead of one large, general-purpose interface, it is better to have several smaller, more granular, client-specific interfaces. This prevents implementing classes from having to create "dummy" or empty implementations for methods they do not need, which is a significant code smell.6

##### **Bad Example (Python)**

The Worker abstract base class is a "fat" interface. It forces the HumanWorker to implement the recharge method and the RobotWorker to implement the eat method, neither of which makes sense for them. This leads to unnecessary and potentially confusing NotImplementedError exceptions.5

Python

\# Bad: "Fat" interface forces clients to implement unused methods  
from abc import ABC, abstractmethod

class Worker(ABC):  
    @abstractmethod  
    def work(self):  
        pass

    @abstractmethod  
    def eat(self):  
        pass

    @abstractmethod  
    def recharge(self):  
        pass

class HumanWorker(Worker):  
    def work(self):  
        print("Human working...")

    def eat(self):  
        print("Human eating...")

    def recharge(self):  
        raise NotImplementedError("Humans don't recharge")

class RobotWorker(Worker):  
    def work(self):  
        print("Robot working...")

    def eat(self):  
        raise NotImplementedError("Robots don't eat")

    def recharge(self):  
        print("Robot recharging...")

##### **Good Example (Python)**

The large Worker interface is segregated into smaller, more specific interfaces (Workable, Feedable, Rechargeable). Classes now only inherit from the abstractions that are relevant to their capabilities. This results in a cleaner, more logical design where no class is forced to implement irrelevant methods.5

Python

\# Good: Interfaces are segregated by role  
from abc import ABC, abstractmethod

class Workable(ABC):  
    @abstractmethod  
    def work(self):  
        pass

class Feedable(ABC):  
    @abstractmethod  
    def eat(self):  
        pass

class Rechargeable(ABC):  
    @abstractmethod  
    def recharge(self):  
        pass

class HumanWorker(Workable, Feedable):  
    def work(self):  
        print("Human working...")

    def eat(self):  
        print("Human eating...")

class RobotWorker(Workable, Rechargeable):  
    def work(self):  
        print("Robot working...")

    def recharge(self):  
        print("Robot recharging...")

##### **Bad Example (TypeScript)**

The PaymentProvider interface is too broad. A CreditCardPaymentProvider has a validate method but no verifyPayment method, while a WalletPaymentProvider is the opposite. Both are forced to implement all methods, leading to "fake" implementations that return false just to satisfy the interface contract.6

TypeScript

// Bad: A single, large interface forces fake implementations  
interface PaymentProvider {  
    validate(): boolean;  
    getPaymentCommission(): number;  
    processPayment(): string;  
    verifyPayment(): boolean;  
}

class CreditCardPaymentProvider implements PaymentProvider {  
    validate(): boolean {  
        console.log("Credit card validated");  
        return true;  
    }  
    getPaymentCommission(): number { return 10; }  
    processPayment(): string { return "cc\_fingerprint"; }  
    verifyPayment(): boolean {  
        // This provider doesn't support verification, but must implement the method  
        return false;  
    }  
}

class WalletPaymentProvider implements PaymentProvider {  
    validate(): boolean {  
        // This provider doesn't support validation, but must implement the method  
        return false;  
    }  
    getPaymentCommission(): number { return 5; }  
    processPayment(): string { return "wallet\_fingerprint"; }  
    verifyPayment(): boolean {  
        console.log("Wallet payment verified");  
        return true;  
    }  
}

##### **Good Example (TypeScript)**

The single PaymentProvider interface is split into three smaller, more focused interfaces: PaymentProcessor, PaymentValidator, and PaymentVerifier. Each class now implements only the interfaces that correspond to its actual capabilities, eliminating the need for fake methods and creating a more honest and maintainable design.6

TypeScript

// Good: Segregated interfaces allow classes to implement only what they need  
interface PaymentProcessor {  
    getPaymentCommission(): number;  
    processPayment(): string;  
}

interface PaymentValidator {  
    validate(): boolean;  
}

interface PaymentVerifier {  
    verifyPayment(): boolean;  
}

class CreditCardPaymentProvider implements PaymentProcessor, PaymentValidator {  
    validate(): boolean {  
        console.log("Credit card validated");  
        return true;  
    }  
    getPaymentCommission(): number { return 10; }  
    processPayment(): string { return "cc\_fingerprint"; }  
}

class WalletPaymentProvider implements PaymentProcessor, PaymentVerifier {  
    getPaymentCommission(): number { return 5; }  
    processPayment(): string { return "wallet\_fingerprint"; }  
    verifyPayment(): boolean {  
        console.log("Wallet payment verified");  
        return true;  
    }  
}

#### **1.1.5. Dependency Inversion Principle (DIP)**

High-level modules, which contain complex logic and policy, should not depend on low-level modules, which handle detailed implementation. Instead, both should depend on abstractions (e.g., interfaces or abstract classes).3 This principle inverts the conventional dependency flow, decoupling the high-level policy from the low-level implementation details, which makes the system more flexible and easier to change.

##### **Bad Example (Python)**

The high-level FrontEnd class is directly dependent on the low-level, concrete BackEnd class. It creates an instance of BackEnd itself. This creates tight coupling. If the data source needs to change (e.g., to an API), the FrontEnd class must be modified, violating both DIP and OCP.5

Python

\# Bad: High-level module depends directly on a low-level module  
class BackEnd:  
    def get\_data\_from\_database(self):  
        return "Data from the database"

class FrontEnd:  
    def \_\_init\_\_(self):  
        self.back\_end \= BackEnd() \# Direct dependency on a concrete class

    def display\_data(self):  
        data \= self.back\_end.get\_data\_from\_database()  
        print("Display data:", data)

##### **Good Example (Python)**

An abstraction, DataSource, is introduced. The FrontEnd class now depends on this abstraction, not on any concrete implementation. The specific data source (e.g., Database or API) is "injected" into the FrontEnd's constructor. This inverts the dependency, decoupling the FrontEnd from the implementation details of how data is fetched.5

Python

\# Good: Both modules depend on an abstraction  
from abc import ABC, abstractmethod

class DataSource(ABC):  
    @abstractmethod  
    def get\_data(self):  
        pass

class Database(DataSource):  
    def get\_data(self):  
        return "Data from the database"

class API(DataSource):  
    def get\_data(self):  
        return "Data from the API"

class FrontEnd:  
    def \_\_init\_\_(self, data\_source: DataSource): \# Depends on the abstraction  
        self.data\_source \= data\_source

    def display\_data(self):  
        data \= self.data\_source.get\_data()  
        print("Display data:", data)

\# The specific dependency is injected at runtime  
db\_frontend \= FrontEnd(Database())  
api\_frontend \= FrontEnd(API())

##### **Bad Example (TypeScript)**

The high-level OrderService is tightly coupled to the low-level MySQLDatabase implementation. If the team decides to switch to a different database, the OrderService class itself will need to be changed.3

TypeScript

// Bad: High-level service is coupled to a low-level concrete implementation  
class MySQLDatabase {  
    public create(order: any): void {  
        console.log("Order created in MySQL");  
    }  
}

class OrderService {  
    private database: MySQLDatabase;

    constructor() {  
        this.database \= new MySQLDatabase(); // Direct instantiation  
    }

    public createOrder(order: any): void {  
        this.database.create(order);  
    }  
}

##### **Good Example (TypeScript)**

A Database interface is introduced as an abstraction. The OrderService now depends on this interface. Concrete implementations like MySQLDatabase and PostgreSQLDatabase implement the interface. The specific database to be used is injected into the OrderService, decoupling the high-level service from the low-level details.3

TypeScript

// Good: High-level service depends on an abstraction (interface)  
interface Database {  
    create(order: any): void;  
}

class MySQLDatabase implements Database {  
    public create(order: any): void {  
        console.log("Order created in MySQL");  
    }  
}

class PostgreSQLDatabase implements Database {  
    public create(order: any): void {  
        console.log("Order created in PostgreSQL");  
    }  
}

class OrderService {  
    private database: Database; // Depends on the interface

    constructor(database: Database) { // The dependency is injected  
        this.database \= database;  
    }

    public createOrder(order: any): void {  
        this.database.create(order);  
    }  
}

// The concrete implementation is chosen at the composition root  
const mysqlService \= new OrderService(new MySQLDatabase());  
const postgresService \= new OrderService(new PostgreSQLDatabase());

### **1.2. Don't Repeat Yourself (DRY)**

Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.8 The DRY principle is aimed at reducing the repetition of code, logic, or information. When applied successfully, a change to a single element of the system does not require changes in other logically unrelated elements.8 The opposite of DRY is often referred to as WET ("Write Everything Twice").11 A useful heuristic for applying DRY is the "Rule of Three": the third time you find yourself repeating a pattern, it's time to abstract it.12

It is crucial to understand that DRY is about the duplication of *knowledge* or *intent*, not just text. Two pieces of code might look identical but represent different business rules; this is coincidental duplication. Forcing such code into a single abstraction creates a false relationship and can lead to bugs when one rule changes but the other does not. The key is to identify true duplication of a single, underlying piece of knowledge. If two code blocks perform the same function because they are bound by the same business rule, they should be unified. If they merely look similar by chance, they should remain separate.

##### **Bad Example (Python)**

The logic for calculating Body Mass Index (BMI) is copied and pasted for each subject. If the BMI formula needs to be corrected or changed, the modification must be made in five different places, which is error-prone and inefficient.13

Python

\# Bad: Repetitive calculation logic (WET code)  
subject1\_data \= \[80, 1.62\]  \# \[weight\_kg, height\_m\]  
subject2\_data \= \[69, 1.53\]  
subject3\_data \= \[80, 1.66\]

bmi\_subject1 \= subject1\_data / (subject1\_data \*\* 2)  
print(f"Subject 1 BMI: {bmi\_subject1:.2f}")

bmi\_subject2 \= subject2\_data / (subject2\_data \*\* 2)  
print(f"Subject 2 BMI: {bmi\_subject2:.2f}")

bmi\_subject3 \= subject3\_data / (subject3\_data \*\* 2)  
print(f"Subject 3 BMI: {bmi\_subject3:.2f}")

##### **Good Example (Python)**

The repeated BMI calculation logic is extracted into a single, reusable function calculate\_bmi. Now, the "knowledge" of how to calculate BMI exists in only one place. Any changes to the formula only need to be made inside this function, ensuring consistency and maintainability.13

Python

\# Good: Logic is abstracted into a reusable function  
def calculate\_bmi(weight\_kg, height\_m):  
    """Calculates BMI from weight in kg and height in meters."""  
    return weight\_kg / (height\_m \*\* 2)

subject1\_data \= \[80, 1.62\]  
subject2\_data \= \[69, 1.53\]  
subject3\_data \= \[80, 1.66\]

bmi\_subject1 \= calculate\_bmi(subject1\_data, subject1\_data)  
print(f"Subject 1 BMI: {bmi\_subject1:.2f}")

bmi\_subject2 \= calculate\_bmi(subject2\_data, subject2\_data)  
print(f"Subject 2 BMI: {bmi\_subject2:.2f}")

bmi\_subject3 \= calculate\_bmi(subject3\_data, subject3\_data)  
print(f"Subject 3 BMI: {bmi\_subject3:.2f}")

##### **Bad Example (TypeScript)**

The logic for calculating a user's age is duplicated across two separate functions, calculateStudentAge and calculateTeacherAge. Although they operate on different types (Student and Teacher), the core logic is identical. This is a duplication of knowledge.14

TypeScript

// Bad: Duplicated age calculation logic  
interface Student {  
    name: string;  
    birthYear: number;  
}

interface Teacher {  
    name: string;  
    birthYear: number;  
}

function calculateStudentAge(student: Student): number {  
    const currentYear \= new Date().getFullYear();  
    return currentYear \- student.birthYear;  
}

function calculateTeacherAge(teacher: Teacher): number {  
    const currentYear \= new Date().getFullYear();  
    return currentYear \- teacher.birthYear;  
}

##### **Good Example (TypeScript)**

A common User interface is created, and a single calculateAge function operates on this interface. This eliminates the duplicated logic. The knowledge of how to calculate age from a birth year is now represented in a single, authoritative location.14

TypeScript

// Good: A single function handles the shared logic  
interface User {  
    name: string;  
    birthYear: number;  
}

function calculateAge(user: User): number {  
    const currentYear \= new Date().getFullYear();  
    return currentYear \- user.birthYear;  
}

const student: User \= { name: 'Alice', birthYear: 2000 };  
const teacher: User \= { name: 'Bob', birthYear: 1985 };

const studentAge \= calculateAge(student);  
const teacherAge \= calculateAge(teacher);

### **1.3. Keep It Simple, Stupid (KISS)**

The KISS principle states that most systems work best if they are kept simple rather than made complicated; therefore, simplicity should be a key goal in design, and unnecessary complexity should be avoided.15 Originating in the U.S. Navy, the principle emphasized that designs must be simple enough for an average mechanic to repair in the field with basic tools.15 In software, this translates to writing code that is easy to read and understand, minimizes moving parts, and avoids overly clever or convoluted solutions that might confuse future developers.17

##### **Bad Example (Python)**

This convert\_temperature function is overly complex. It uses a deeply nested if/elif structure to handle all possible conversion paths. As more temperature scales are added, the complexity of this single function would grow exponentially, making it difficult to read, test, and maintain.18

Python

\# Bad: Overly complex and nested conditional logic  
def convert\_temperature(value, unit\_from, unit\_to):  
    if unit\_from \== 'celsius':  
        if unit\_to \== 'fahrenheit':  
            return (value \* 9/5) \+ 32  
        elif unit\_to \== 'kelvin':  
            return value \+ 273.15  
    elif unit\_from \== 'fahrenheit':  
        if unit\_to \== 'celsius':  
            return (value \- 32) \* 5/9  
        elif unit\_to \== 'kelvin':  
            return ((value \- 32) \* 5/9) \+ 273.15  
    \#... and so on for other combinations  
    return None

##### **Good Example (Python)**

The logic is simplified by breaking it down. A dictionary is used to map conversion pairs to simple lambda functions. This approach is flatter, more declarative, and much easier to extend. To add a new conversion, one only needs to add a new entry to the dictionary, without increasing the logical complexity of the main function.18

Python

\# Good: Simple, declarative, and easy to extend  
def convert\_temperature(value, unit\_from, unit\_to):  
    if unit\_from \== unit\_to:  
        return value

    conversions \= {  
        ('celsius', 'fahrenheit'): lambda v: (v \* 9/5) \+ 32,  
        ('celsius', 'kelvin'): lambda v: v \+ 273.15,  
        ('fahrenheit', 'celsius'): lambda v: (v \- 32) \* 5/9,  
        ('fahrenheit', 'kelvin'): lambda v: ((v \- 32) \* 5/9) \+ 273.15,  
        ('kelvin', 'celsius'): lambda v: v \- 273.15,  
        ('kelvin', 'fahrenheit'): lambda v: ((v \- 273.15) \* 9/5) \+ 32,  
    }

    conversion\_func \= conversions.get((unit\_from, unit\_to))  
    if conversion\_func:  
        return conversion\_func(value)  
    else:  
        raise ValueError("Unsupported temperature conversion")

##### **Bad Example (TypeScript)**

The getUserStatus function is hard to read due to deep nesting of if/else statements. The cognitive load required to trace all possible execution paths is high, making the code prone to errors and difficult to modify.19

TypeScript

// Bad: Deeply nested logic is hard to follow  
function getUserStatus(user: { age: number, isActive: boolean } | null): string {  
    if (user) {  
        if (user.age \>= 18) {  
            if (user.isActive) {  
                return 'Active Adult';  
            } else {  
                return 'Inactive Adult';  
            }  
        } else {  
            if (user.isActive) {  
                return 'Active Minor';  
            } else {  
                return 'Inactive Minor';  
            }  
        }  
    }  
    return 'Unknown';  
}

##### **Good Example (TypeScript)**

The function is refactored to be simpler and flatter. An early return (a "guard clause") handles the null case. Ternary operators are then used to determine the status parts, which are combined at the end. This version is much more direct and easier to understand at a glance.19

TypeScript

// Good: Flatter, more readable logic  
function getUserStatus(user: { age: number, isActive: boolean } | null): string {  
    if (\!user) {  
        return 'Unknown';  
    }

    const ageStatus \= user.age \>= 18? 'Adult' : 'Minor';  
    const activityStatus \= user.isActive? 'Active' : 'Inactive';

    return \`${activityStatus} ${ageStatus}\`;  
}

### **1.4. You Aren't Gonna Need It (YAGNI)**

A principle from eXtreme Programming, YAGNI states that you should always implement things when you actually need them, never when you just foresee that you may need them.20 It advises against adding functionality or complexity in anticipation of future needs that may never materialize, thus avoiding the costs of over-engineering, such as increased maintenance, complexity, and potential for bugs.21

YAGNI is often misinterpreted as a call for short-sighted design. In reality, it is a risk mitigation strategy that preserves flexibility and enables agility. The future is uncertain, and building a feature for a predicted future that never arrives is wasted effort. By implementing only what is needed now, the codebase remains smaller, simpler, and easier to change. This does not mean "don't think about the future," but rather "don't *code* for the future." A good design, following principles like SOLID, makes the system easy to extend when new requirements emerge. YAGNI ensures you don't pay the cost of a change until that change is actually required.

##### **Bad Example (Python)**

A developer building a notification system anticipates needing to send notifications via email, SMS, push, Slack, Teams, and webhooks. They build a complex, generic OverengineeredNotification class that handles all these channels, user preferences, and delivery scheduling from the start, even though the current requirement is only for email notifications.23 This adds significant complexity for features that are not currently needed.

Python

\# Bad: Building features for a speculative future  
class OverengineeredNotification:  
    def \_\_init\_\_(self):  
        \# A large number of features that are not currently required  
        self.channels \= {'email': True, 'sms': False, 'push': False, 'slack': False}  
        self.user\_preferences \= {}  
        self.delivery\_schedule \= {}  
        self.templates \= {}  
        self.notification\_history \=

    def send(self, user, message, channel='email', priority='normal', schedule\_time=None):  
        \# Complex logic to handle scheduling, preferences, multiple channels, etc.  
        if channel \== 'email' and self.channels\['email'\]:  
            print(f"Sending email to {user}: {message}")  
        \#... plus complex, unused logic for all other channels  
        self.\_log\_notification(user, channel, message)

    def \_log\_notification(self, user, channel, message):  
        self.notification\_history.append({  
            'user': user,  
            'channel': channel,  
            'message': message,  
            'timestamp': 'some\_timestamp'  
        })

##### **Good Example (Python)**

The developer implements only what is needed now: a simple class for sending email notifications. The design is kept clean and simple, making it easy to extend later if and when support for other notification channels is actually required. This saves time and avoids unnecessary complexity.23

Python

\# Good: Implementing only the currently required functionality  
class EmailNotifier:  
    def \_\_init\_\_(self):  
        \# Simple, focused state  
        self.history \=

    def send(self, user, message):  
        """Sends an email notification."""  
        print(f"Sending email to {user}: {message}")  
        self.\_log\_email(user, message)

    def \_log\_email(self, user, message):  
        self.history.append({'user': user, 'message': message})

\# If SMS is needed later, a new class or method can be added then.

##### **Bad Example (TypeScript)**

A developer is building a simple application that needs to make HTTP GET and POST requests. Anticipating that the application might need other HTTP methods in the future, they build a comprehensive HttpClient class that includes GET, POST, PUT, PATCH, and DELETE methods from the outset. This is a classic YAGNI violation.24

TypeScript

// Bad: Over-engineered client with methods that are not currently needed  
class HttpClient {  
    public get\<T\>(url: string): Promise\<T\> {  
        console.log(\`Fetching from ${url}\`);  
        return Promise.resolve({} as T);  
    }  
    public post\<T\>(url:string, body: any): Promise\<T\> {  
        console.log(\`Posting to ${url}\`);  
        return Promise.resolve({} as T);  
    }  
    public put\<T\>(url:string, body: any): Promise\<T\> {  
        // We don't need this yet, but building it just in case  
        console.log(\`Putting to ${url}\`);  
        return Promise.resolve({} as T);  
    }  
    public patch\<T\>(url:string, body: any): Promise\<T\> {  
        // We don't need this yet, but building it just in case  
        console.log(\`Patching ${url}\`);  
        return Promise.resolve({} as T);  
    }  
    public delete\<T\>(url:string): Promise\<T\> {  
        // We don't need this yet, but building it just in case  
        console.log(\`Deleting ${url}\`);  
        return Promise.resolve({} as T);  
    }  
}

##### **Good Example (TypeScript)**

The developer implements an HttpClient with only the methods that are currently required by the application: get and post. The other methods can be added later if a new feature requires them. This approach keeps the codebase lean and focused on delivering current requirements.24

TypeScript

// Good: Start with a lean implementation of only what's needed now  
class HttpClient {  
    public get\<T\>(url: string): Promise\<T\> {  
        console.log(\`Fetching from ${url}\`);  
        return Promise.resolve({} as T);  
    }  
    public post\<T\>(url:string, body: any): Promise\<T\> {  
        console.log(\`Posting to ${url}\`);  
        return Promise.resolve({} as T);  
    }  
}

// Add put, patch, and delete methods only when the application actually needs them.

## **2\. Code Quality & Readability**

This section focuses on the fine-grained details of writing code that is clean, expressive, and easy for other humans to understand. While architectural principles define the structure, these practices define the quality of the implementation within that structure.

### **2.1. Naming Conventions**

Names in code (variables, functions, classes) should be meaningful, descriptive, and consistent. They should reveal their intent, making the code self-documenting and reducing the need for explanatory comments.26 Avoid single-letter names unless their scope is very small and their meaning is obvious (e.g.,

i in a loop), and avoid abbreviations or mental mapping that obscure meaning.26 A centralized reference for naming conventions is invaluable for promoting consistency across the entire codebase.

| Identifier Type | Python Convention (PEP 8\) | Python Example | TypeScript Convention | TypeScript Example |
| :---- | :---- | :---- | :---- | :---- |
| Variable | snake\_case | user\_name | camelCase | userName |
| Constant | UPPER\_CASE\_WITH\_UNDERSCORES | MAX\_RETRIES | UPPER\_CASE\_WITH\_UNDERSCORES | MAX\_RETRIES |
| Function/Method | snake\_case | calculate\_total() | camelCase | calculateTotal() |
| Class | PascalCase | UserManager | PascalCase | UserManager |
| Interface | N/A | N/A | PascalCase | IUser or User |
| Type Alias | PascalCase | Vector \= list\[float\] | PascalCase | type UserId \= string; |
| Module/File | snake\_case.py | user\_service.py | kebab-case.ts | user-service.ts |

### **2.2. Function Size and Complexity**

Functions should be small and adhere to the Single Responsibility Principle: they should do one thing and do it well.27 While there are differing opinions on strict line counts, with some advocating for functions under 20 lines 29, the guiding principle is functional coherence. A function should represent a single, complete unit of logic.29 Signs that a function may be too large or complex include multiple levels of indentation or blank lines separating distinct logical blocks within the function body.30

The drive for small functions is a powerful technique for managing levels of abstraction. A large function often mixes high-level policy with low-level implementation details, making it difficult to read. By extracting low-level details into smaller, well-named functions, the main function becomes a clean, readable summary of the high-level logic. This "Extract Method" refactoring technique gives a name to a concept, reduces the cognitive load on the reader, and makes the overall algorithm clearer.31

##### **Bad Example (Python)**

The process\_order function is doing too much: it validates the order, calculates the total, applies a discount, and generates a receipt. Its multiple responsibilities make it long, hard to read, and difficult to test or modify in isolation.32

Python

\# Bad: This function has multiple responsibilities  
def process\_order(order):  
    \# 1\. Validate order  
    if not order.get("items"):  
        return "Order must contain items"  
      
    \# 2\. Calculate total price  
    total \= sum(item\["price"\] \* item\["quantity"\] for item in order\["items"\])  
      
    \# 3\. Apply discount  
    if order.get("discount\_code") \== "SAVE10":  
        total \*= 0.9  
          
    \# 4\. Generate receipt  
    receipt \= f"Total: ${total:.2f}"  
    return receipt

##### **Good Example (Python)**

The original function is refactored into several smaller functions, each with a single responsibility. The new process\_order function now orchestrates calls to these helper functions. Its logic is clear and reads like a high-level summary of the process. Each individual step is now independently testable and reusable.32

Python

\# Good: Responsibilities are extracted into smaller, focused functions  
def validate\_order(order):  
    if not order.get("items"):  
        raise ValueError("Order must contain items")

def calculate\_total(order):  
    return sum(item\["price"\] \* item\["quantity"\] for item in order\["items"\])

def apply\_discount(total, discount\_code):  
    if discount\_code \== "SAVE10":  
        return total \* 0.9  
    return total

def generate\_receipt(total):  
    return f"Total: ${total:.2f}"

def process\_order(order):  
    try:  
        validate\_order(order)  
        total \= calculate\_total(order)  
        total\_after\_discount \= apply\_discount(total, order.get("discount\_code"))  
        return generate\_receipt(total\_after\_discount)  
    except ValueError as e:  
        return str(e)

##### **Bad Example (TypeScript)**

The computeScore function contains repeated logic (player.power \- monster) and mixes the conditional check with the calculation. While short, its internal logic could be clearer and more expressive.33

TypeScript

// Bad: Logic is tangled and contains repetition  
function computeScore(player: { power: number }, monsters: number): number {  
    let score: number \= 0;  
    for (const monster of monsters) {  
        if (player.power \> monster) {  
            score \+= player.power \- monster;  
        } else {  
            // The logic here is inverted, which can be confusing  
            score \-= monster \- player.power;  
        }  
    }  
    return score;  
}

##### **Good Example (TypeScript)**

The core scoring logic is extracted into a new, pure function called calculateScoreChange. This function has a single, clear purpose. The main computeGameScore function now becomes simpler and more readable, as it focuses on iterating and accumulating the score, delegating the complex calculation to the helper function.33

TypeScript

// Good: Core logic is extracted into a focused helper function  
function calculateScoreChange(playerPower: number, monsterPower: number): number {  
    // This function now has one responsibility: calculate the score delta  
    return playerPower \- monsterPower;  
}

function computeGameScore(player: { power: number }, monsters: number): number {  
    let score: number \= 0;  
    for (const monster of monsters) {  
        score \+= calculateScoreChange(player.power, monster);  
    }  
    return score;  
}

### **2.3. Comments: The "Why," Not the "What"**

The best code is self-documenting. Comments should be viewed as a last resort, used to compensate for a failure to express an idea in the code itself.34 If you feel the need to write a comment, first attempt to refactor the code to make it clearer.34 Comments should explain the "why"—the intent, the rationale behind a non-obvious decision, or a warning about consequences—not the "what," which the code should already make clear.34 Bad comments, such as those that are redundant, misleading, or simply state the obvious, add clutter and can become outdated, propagating misinformation.36

##### **Bad Example (Python)**

This code uses comments to explain *what* the code is doing. The variable names are cryptic (emp\_flg, yoe), and the logic is unclear without the comments. This is a classic case of commenting bad code instead of rewriting it.

Python

\# Bad: Comments explain WHAT the code is doing, because the code is unclear  
def check\_eligibility(employee):  
    \# Check if employee has been with the company for more than 2 years  
    if employee.yoe \> 2:  
        \# Check if employee has the high-performance flag set  
        if employee.emp\_flg & 0x10:  
            return True  
    return False

##### **Good Example (Python)**

The code is refactored to be self-documenting. Variables and constants are given clear, descriptive names. The logic is encapsulated in a well-named function. Now, a comment is only needed to explain the *why*—the non-obvious business reason for a specific magic number.

Python

\# Good: Code is self-documenting; comment explains WHY  
HIGH\_PERFORMANCE\_FLAG \= 0x10

def is\_bonus\_eligible(employee):  
    """Checks if an employee is eligible for the annual performance bonus."""  
      
    \# Per HR policy, bonus eligibility requires the high-performance flag.  
    \# This was a temporary measure for the Q4 assessment cycle.  
    \# TODO: Re-evaluate this policy for the next fiscal year (TICKET-123).  
    has\_high\_performance\_flag \= employee.flags & HIGH\_PERFORMANCE\_FLAG  
      
    is\_long\_term\_employee \= employee.years\_of\_experience \> 2  
      
    return is\_long\_term\_employee and has\_high\_performance\_flag

##### **Bad Example (TypeScript)**

This comment explains *what* the regular expression does. While potentially helpful, it's a sign that the code itself is not expressive. The regex is a "magic" value embedded directly in the logic.

TypeScript

// Bad: Comment explains the "what" of a complex regex  
function isValidDate(dateString: string): boolean {  
    // Checks if the string is in YYYY-MM-DD format  
    const regex \= /^\\d{4}-\\d{2}-\\d{2}$/;  
    return regex.test(dateString);  
}

##### **Good Example (TypeScript)**

The regular expression is extracted into a constant with a descriptive name, making the code self-explanatory. The need for the "what" comment is eliminated. A new comment is added to explain the "why"—the reason for a specific, non-obvious design choice (e.g., why a third-party API requires this specific format).

TypeScript

// Good: Self-documenting code; comment explains the "why"  
const DATE\_FORMAT\_YYYY\_MM\_DD \= /^\\d{4}-\\d{2}-\\d{2}$/;

function isValidDate(dateString: string): boolean {  
    // The legacy reporting API requires dates to be in YYYY-MM-DD format.  
    // We must validate this format on the client-side before sending the request.  
    return DATE\_FORMAT\_YYYY\_MM\_DD.test(dateString);  
}

## **3\. Security Best Practices**

Security is not an optional feature or a final step in the development process; it is a fundamental aspect of software quality. These practices are designed to be integrated into the daily development workflow to build secure systems by default.

### **3.1. OWASP Top 10 Summary**

The OWASP Top 10 is a standard awareness document that represents a broad consensus on the most critical security risks to web applications.38 All developers must be familiar with these risks and actively work to mitigate them in their code and designs. The list is updated periodically to reflect the changing threat landscape; the following table summarizes the 2021 edition, which is the most recent for general web applications.39

| ID | Vulnerability | Brief Description |
| :---- | :---- | :---- |
| A01:2021 | Broken Access Control | Flaws in enforcing permissions, allowing users to act outside their intended access levels (e.g., viewing another user's data). |
| A02:2021 | Cryptographic Failures | Failures related to cryptography (e.g., weak algorithms, improper key management), often leading to the exposure of sensitive data. |
| A03:2021 | Injection | Flaws that allow untrusted data to be sent to an interpreter as part of a command or query (e.g., SQL, NoSQL, OS command injection). |
| A04:2021 | Insecure Design | Risks related to fundamental design flaws or missing security controls, which cannot be fixed by a perfect implementation. |
| A05:2021 | Security Misconfiguration | Missing or insecure configurations in the application stack, such as default credentials, open cloud storage, or verbose error messages. |
| A06:2021 | Vulnerable and Outdated Components | Using libraries, frameworks, or other software modules with known vulnerabilities (e.g., from an unpatched third-party dependency). |
| A07:2021 | Identification and Authentication Failures | Incorrect implementation of functions related to user identity, authentication, and session management, leading to account takeover. |
| A08:2021 | Software and Data Integrity Failures | Flaws related to code and infrastructure that do not protect against integrity violations (e.g., insecure deserialization). |
| A09:2021 | Security Logging and Monitoring Failures | Insufficient logging, monitoring, or alerting to detect and respond to security incidents in a timely manner. |
| A10:2021 | Server-Side Request Forgery (SSRF) | Flaws allowing an attacker to induce the server-side application to make requests to an unintended location, often an internal service. |

### **3.2. Input Validation**

All external input is untrusted and must be validated before use. This includes data from users, other internal services, and third-party APIs. Validation is the first line of defense against many common vulnerabilities, including injection attacks. It ensures that data is of the correct type, within an acceptable range, in the proper format, and sanitized of malicious content.41 Validation logic should be centralized rather than scattered throughout the application.44 When validation fails, the system should return a clear, generic error message that does not reveal sensitive system details.41

##### **Bad Example (Python)**

This code directly uses user input to construct a database query. It fails to validate or sanitize the user\_id, making it vulnerable to SQL Injection. An attacker could provide a malicious string like 123 OR 1=1 to bypass authentication.

Python

\# Bad: No input validation, vulnerable to SQL Injection  
import sqlite3

def get\_user\_data(user\_id: str):  
    \# This is extremely dangerous\! Never format queries with user input.  
    query \= f"SELECT \* FROM users WHERE id \= {user\_id}"  
      
    conn \= sqlite3.connect('database.db')  
    cursor \= conn.cursor()  
    cursor.execute(query)  
    return cursor.fetchone()

##### **Good Example (Python)**

This example demonstrates proper input validation and secure database practices. It first validates that the input is an integer using a try-except block. Then, it uses a parameterized query (? placeholder), which is the standard way to prevent SQL Injection. The database driver handles the safe substitution of the value, ensuring it is treated as data, not executable code.42

Python

\# Good: Input is validated and a parameterized query is used  
import sqlite3  
import re

def validate\_email(email: str):  
    """Validates email format using regex."""  
    email\_pattern \= r'^\[a-zA-Z0-9\_.+-\]+@\[a-zA-Z0-9-\]+\\.\[a-zA-Z0-9-.\]+$'  
    if not re.match(email\_pattern, email):  
        raise ValueError("Invalid email format.")

def get\_user\_data(user\_id\_str: str):  
    try:  
        \# Type and Range Validation  
        user\_id \= int(user\_id\_str)  
        if user\_id \<= 0:  
            raise ValueError("User ID must be a positive number.")  
    except ValueError:  
        raise ValueError("Invalid User ID provided.")

    \# Use parameterized queries to prevent SQL Injection  
    query \= "SELECT \* FROM users WHERE id \=?"  
      
    conn \= sqlite3.connect('database.db')  
    cursor \= conn.cursor()  
    cursor.execute(query, (user\_id,))  
    return cursor.fetchone()

##### **Bad Example (TypeScript)**

This code takes a raw object and assumes it matches the User type without any runtime validation. If the incoming data object is missing properties or has properties of the wrong type (e.g., from a malicious API response or user input), it can lead to runtime errors or unexpected behavior when processUser is called.

TypeScript

// Bad: No runtime validation, assumes input matches the type  
interface User {  
    id: number;  
    username: string;  
    email: string;  
}

function processUser(user: User) {  
    console.log(\`Processing user: ${user.username.toLowerCase()}\`);  
}

// This function trusts that the input data conforms to the User interface  
function handleRequest(data: any) {  
    const user: User \= data; // Unsafe type assertion  
    processUser(user); // This could crash if data.username is not a string  
}

##### **Good Example (TypeScript)**

Using a library like Zod, a schema is defined that serves as a single source of truth for both the static TypeScript type and the runtime validation logic. The bookValidator.parse(data) call will throw an error if the runtime data does not conform to the schema, preventing unsafe data from propagating through the system. This approach ensures that types and validation logic never drift out of sync.46

TypeScript

// Good: Zod schema provides both static types and runtime validation  
import { z } from 'zod';

// Define a schema for validation  
const UserSchema \= z.object({  
    id: z.number().positive(),  
    username: z.string().min(3),  
    email: z.string().email(),  
});

// Infer the TypeScript type from the schema  
type User \= z.infer\<typeof UserSchema\>;

function processUser(user: User) {  
    console.log(\`Processing user: ${user.username.toLowerCase()}\`);  
}

// This function validates the input data at runtime before processing  
function handleRequest(data: unknown) {  
    try {  
        const user \= UserSchema.parse(data); // Throws an error if data is invalid  
        processUser(user);  
    } catch (error) {  
        console.error("Validation failed:", error);  
        // Handle invalid data appropriately  
    }  
}

### **3.3. Principle of Least Privilege (PoLP)**

A user, process, or application should only have the minimum permissions necessary to perform its intended function.47 This is a foundational concept of Zero Trust security that limits the potential damage from a security breach by minimizing the attack surface. PoLP is often implemented using Role-Based Access Control (RBAC), where permissions are assigned to roles (e.g., 'admin', 'editor', 'viewer') rather than directly to individual users.49 This principle must be enforced at every layer of the application, not just at the infrastructure level. The application code must be authorization-aware, verifying permissions for every sensitive operation.

##### **Bad Example (Python)**

This example has a single api\_call function that performs actions based on a string command. There is no concept of roles or permissions. Any authenticated user who can call this function could potentially delete data, even if their role should only allow them to read it. The function is over-privileged.

Python

\# Bad: No role-based access control; any user can perform any action  
class API:  
    def \_\_init\_\_(self, user):  
        self.user \= user  
        self.data \= {"key": "value"}

    def perform\_action(self, action, key, value=None):  
        if action \== "read":  
            return self.data.get(key)  
        elif action \== "write":  
            self.data\[key\] \= value  
            return "Write successful"  
        elif action \== "delete":  
            if key in self.data:  
                del self.data\[key\]  
                return "Delete successful"  
        return "Unknown action"

##### **Good Example (Python)**

This implementation introduces a simple RBAC system. Roles are defined with specific, granular permissions. The has\_access function checks if a user's role grants them the required permission for an action. Each method in the API class now checks for the appropriate permission before executing the operation, enforcing the Principle of Least Privilege.49

Python

\# Good: Enforces least privilege using Role-Based Access Control (RBAC)  
ROLES \= {  
    "viewer": \["read"\],  
    "editor": \["read", "write"\],  
    "admin": \["read", "write", "delete"\]  
}

def has\_access(user\_role, required\_permission):  
    """Checks if a user's role includes the required permission."""  
    if user\_role in ROLES and required\_permission in ROLES\[user\_role\]:  
        return True  
    return False

class User:  
    def \_\_init\_\_(self, name, role):  
        if role not in ROLES:  
            raise ValueError("Invalid role specified")  
        self.name \= name  
        self.role \= role

class API:  
    def \_\_init\_\_(self):  
        self.data \= {"key": "sensitive\_value"}  
          
    def read\_data(self, user: User, key: str):  
        if has\_access(user.role, "read"):  
            return self.data.get(key)  
        else:  
            raise PermissionError("User does not have 'read' permission")

    def write\_data(self, user: User, key: str, value: str):  
        if has\_access(user.role, "write"):  
            self.data\[key\] \= value  
            return "Write successful"  
        else:  
            raise PermissionError("User does not have 'write' permission")

##### **Bad Example (TypeScript)**

In this Express.js application, the admin endpoint only checks if a user is logged in (req.session.userId). It does not check if the user has the 'admin' role. Any authenticated user, regardless of their privilege level, could access this sensitive route.

TypeScript

// Bad: Endpoint only checks for authentication, not authorization (role)  
import express from 'express';  
// Assume session middleware is configured

const router \= express.Router();

router.get('/admin/dashboard', (req, res) \=\> {  
    // This check is insufficient. It only confirms the user is logged in.  
    if (\!req.session.userId) {  
        return res.status(401).json({ error: 'Unauthorized' });  
    }  
      
    // Any logged-in user can access the admin dashboard  
    res.json({ message: 'Welcome to the admin dashboard\!' });  
});

##### **Good Example (TypeScript)**

A requireRole middleware is introduced. This middleware is a higher-order function that takes a required role as an argument. Before granting access to the route handler, it checks not only for authentication but also verifies that the user's role matches the required role. This ensures that only users with the 'admin' role can access the /admin/dashboard endpoint, correctly implementing PoLP.50

TypeScript

// Good: Middleware enforces role-based access control  
import express, { Request, Response, NextFunction } from 'express';  
// Assume User model and session middleware are configured  
// interface User { id: number; username: string; role: 'admin' | 'viewer'; }  
// declare module 'express-session' { interface SessionData { userId: number; userRole: string; } }

const router \= express.Router();

const requireRole \= (role: string) \=\> {  
    return (req: Request, res: Response, next: NextFunction) \=\> {  
        if (\!req.session.userId) {  
            return res.status(401).json({ error: 'Unauthorized' });  
        }  
          
        // Check if the user's role from the session matches the required role  
        if (req.session.userRole\!== role) {  
            return res.status(403).json({ error: 'Forbidden' });  
        }  
          
        next();  
    };  
};

// The route is now protected by the RBAC middleware  
router.get('/admin/dashboard', requireRole('admin'), (req, res) \=\> {  
    res.json({ message: 'Welcome, Admin\!' });  
});

router.get('/profile', (req, res) \=\> {  
    // A general route accessible by any authenticated user  
    if (\!req.session.userId) {  
        return res.status(401).json({ error: 'Unauthorized' });  
    }  
    res.json({ message: 'This is your profile page.' });  
});

## **4\. Testing Methodologies**

A robust testing strategy is essential for building reliable software. It provides a safety net for refactoring, verifies that the system meets its requirements, and gives the team confidence to deploy changes frequently.

### **4.1. Unit vs. Integration Testing**

**Unit Testing** focuses on testing the smallest testable parts of an application—a "unit," such as a single function or class—in complete isolation from other parts. To achieve this isolation, external dependencies like databases, network services, or other classes are typically replaced with test doubles (mocks or stubs). The goal is to verify that the unit's internal logic works correctly. Unit tests should be fast, deterministic, and form the largest portion of a project's test suite.51

**Integration Testing** verifies that different modules, services, or components of an application work together correctly when they are combined. It focuses on testing the interactions, interfaces, and data flow between these integrated units.51 Unlike unit tests, integration tests are broader in scope and may involve real dependencies to simulate real-world scenarios. They are slower to run but are critical for uncovering issues that only appear when different parts of the system interact.54

Martin Fowler notes that the term "integration test" can be ambiguous and distinguishes between "narrow" integration tests (which test the interaction with a service using a test double) and "broad" integration tests (which use live versions of all services, akin to end-to-end tests).56 Similarly, he distinguishes between "solitary" unit tests (which mock all collaborators) and "sociable" unit tests (which may use real collaborators if they are fast and deterministic).58

| Aspect | Unit Testing | Integration Testing |
| :---- | :---- | :---- |
| **Scope** | A single unit (function, class) in isolation. | Multiple components interacting together. |
| **Focus** | Internal logic of the unit (White-box). | Interfaces and data flow between components (Black-box). |
| **Dependencies** | External dependencies are mocked or stubbed. | May use real dependencies (database, API calls). |
| **Speed** | Very fast. | Slower due to broader scope and real dependencies. |
| **Debugging** | Failures are easy to pinpoint to the specific unit. | Failures can be harder to trace to the root cause. |

### **4.2. Test-Driven Development (TDD): The Red-Green-Refactor Cycle**

Test-Driven Development (TDD) is a software development process where you write a failing automated test *before* you write the code to make it pass. This process is driven by a short, repetitive cycle known as "Red-Green-Refactor".60

The primary benefit of TDD is not just achieving high test coverage, but driving better software design. To write a test for code before it exists, one must first consider its public API from the perspective of a client. This naturally leads to more usable and intuitive APIs. Furthermore, to make code testable in isolation—a prerequisite for TDD—it must be decoupled from its dependencies, encouraging adherence to principles like Dependency Inversion. The comprehensive test suite is a valuable byproduct of this design-centric process.

The cycle consists of three phases:

1. **Red**: Write a small test for a specific piece of functionality that does not yet exist. Run the test and confirm that it fails for the expected reason (e.g., the function is not defined, or the assertion fails). This step is crucial to verify that the test itself is working correctly.61  
2. **Green**: Write the absolute minimum amount of code necessary to make the test pass. The goal here is not elegance or optimization but simply to get to a passing state as quickly as possible.61  
3. **Refactor**: With the safety net of a passing test, improve the design of the code you just wrote. Clean up duplication, improve names, simplify logic, and enhance the structure, all while continuously running the test to ensure it remains green.61

##### **TDD Cycle Example (Python)**

Let's develop a function calculate\_total for a shopping cart.

1\. Red: Write a failing test.  
The test assumes a function calculate\_total that takes a list of item prices and returns their sum. This test will fail because the function doesn't exist yet.

Python

\# test\_cart.py  
import unittest  
from cart import calculate\_total \# This import will fail initially

class TestCart(unittest.TestCase):  
    def test\_calculate\_total\_of\_empty\_cart(self):  
        self.assertEqual(calculate\_total(), 0)

    def test\_calculate\_total\_with\_items(self):  
        self.assertEqual(calculate\_total(\[10.0, 20.5, 5.0\]), 35.5)

\# Running this test results in an ImportError or NameError: RED

2\. Green: Write the minimal code to pass.  
Create the calculate\_total function with the simplest possible implementation that satisfies the tests.

Python

\# cart.py  
def calculate\_total(prices):  
    total \= 0  
    for price in prices:  
        total \+= price  
    return total

\# Running the tests now results in them passing: GREEN

3\. Refactor: Improve the code.  
The current implementation is simple but can be made more concise and "Pythonic" by using the built-in sum() function. The tests ensure this refactoring doesn't break the functionality.60

Python

\# cart.py  
def calculate\_total(prices):  
    """Calculates the total price of items."""  
    return sum(prices)

\# Running the tests again confirms they still pass: REFACTOR (and still GREEN)

##### **TDD Cycle Example (TypeScript with Jest)**

Let's develop a Dictionary class.

1\. Red: Write a failing test.  
We start by testing the size() method. The test expects a new dictionary to have a size of 0\. This will fail because the Dictionary class and its size method do not exist.

TypeScript

// Dictionary.test.ts  
import { Dictionary } from './Dictionary'; // This import will fail

describe('Dictionary', () \=\> {  
    it('should have a size of 0 when created', () \=\> {  
        const dictionary \= new Dictionary\<string\>();  
        expect(dictionary.size()).toBe(0);  
    });  
});

// Running this test results in an error: RED

2\. Green: Write the minimal code to pass.  
Create the Dictionary class with a size method that returns a hardcoded 0 to make the test pass as quickly as possible.63

TypeScript

// Dictionary.ts  
export class Dictionary\<T\> {  
    public size(): number {  
        return 0;  
    }  
}

// Running the test now results in it passing: GREEN

3\. Refactor: Improve the code.  
Now, let's add a test for the put method.  
Red:

TypeScript

// Dictionary.test.ts (add new test)  
it('should have a size of 1 after adding an item', () \=\> {  
    const dictionary \= new Dictionary\<string\>();  
    dictionary.put('key1', 'value1');  
    expect(dictionary.size()).toBe(1);  
});

This new test fails.  
Green:  
We implement the put method and a private property to track the items.

TypeScript

// Dictionary.ts  
export class Dictionary\<T\> {  
    private items: { \[key: string\]: T } \= {};  
    private count: number \= 0;

    public put(key: string, value: T): void {  
        this.items\[key\] \= value;  
        this.count++;  
    }

    public size(): number {  
        return this.count;  
    }  
}

All tests now pass.  
Refactor: The code is reasonably clean for this stage. We can now continue this cycle for get, remove, and other methods.

## **5\. Version Control Best Practices**

Effective use of version control is crucial for team collaboration, maintaining a clean and understandable project history, and enabling automation in the CI/CD pipeline.

### **5.1. Conventional Commits**

The Conventional Commits specification is a lightweight convention on top of commit messages that provides a simple set of rules for creating an explicit and machine-readable commit history. This structure helps automate processes like semantic versioning and changelog generation.64

The structure of a conventional commit message is as follows:

\<type\>\[optional scope\]: \<description\>

\[optional body\]

\[optional footer(s)\]

* **type**: A mandatory prefix indicating the nature of the change. Common types include 65:  
  * feat: A new feature for the user. (Correlates with a MINOR version bump in SemVer).  
  * fix: A bug fix for the user. (Correlates with a PATCH version bump in SemVer).  
  * docs: Documentation only changes.  
  * style: Changes that do not affect the meaning of the code (white-space, formatting, etc.).  
  * refactor: A code change that neither fixes a bug nor adds a feature.  
  * perf: A code change that improves performance.  
  * test: Adding missing tests or correcting existing tests.  
  * build: Changes that affect the build system or external dependencies.  
  * ci: Changes to our CI configuration files and scripts.  
  * chore: Other changes that don't modify source or test files.  
* **scope** (optional): A noun in parentheses providing context for the change (e.g., api, auth, ui).67  
* **description**: A short, imperative summary of the code change.  
* **body** (optional): A longer, more detailed explanation of the change, providing context and reasoning.  
* **footer(s)** (optional): Contains metadata, such as issue tracker references (e.g., Fixes: \#123) or breaking change notifications.  
* **Breaking Changes**: A commit that introduces a breaking API change must be indicated by appending a \! after the type(scope) prefix, or by adding a footer starting with BREAKING CHANGE:.66 This correlates with a  
  MAJOR version bump in SemVer.

**Example Commits:**

// Simple feature commit  
feat(auth): add password reset functionality

// Commit with a scope and body  
fix(api): correct pagination query parameter

The \`offset\` parameter was being ignored in the user list endpoint.  
This change ensures it is correctly applied to the database query.  
Fixes: \#245

// Commit with a breaking change  
refactor(user)\!: rename User.id to User.uuid

BREAKING CHANGE: The \`id\` field on the User model has been replaced  
with \`uuid\` to conform to the new database schema. All clients  
consuming the user API must be updated.

Adopting this convention enables the use of a rich ecosystem of tools for validation (commitlint), interactive committing (commitizen), and automated releases and changelogs (semantic-release).68

## **6\. Practices for the Specified Technology Stack**

This section provides specific best practices, conventions, and tooling recommendations for our primary technology stack: Python and TypeScript.

### **6.1. Python Best Practices**

#### **6.1.1. Writing "Pythonic" Code**

"Pythonic" code uses the language's features and idioms as intended, favoring readability, simplicity, and explicitness. It is about writing code that aligns with the philosophy outlined in "The Zen of Python" (PEP 20), which can be viewed by running import this in a Python interpreter.70

Key idioms to embrace include:

* **Comprehensions and Generator Expressions**: Use list, set, and dictionary comprehensions for creating collections from iterables. They are more concise and often faster than explicit for loops. For large datasets where the entire collection is not needed in memory at once, use generator expressions.70  
* **Context Managers (with statement)**: Always use the with statement for managing resources like files or database connections. It guarantees that cleanup logic (like closing the file) is executed, even if errors occur within the block.71  
* **Truth Value Testing**: Leverage Python's concept of truthiness for cleaner conditional checks. For example, check for an empty list with if my\_list: instead of if len(my\_list) \> 0\. However, for None, always use the explicit if my\_var is None:.73  
* **Unpacking**: Use tuple and dictionary unpacking for more elegant and readable assignments and function calls. For example, a, b \= b, a for swapping variables.70

#### **6.1.2. Virtual Environments with venv**

Always use a virtual environment for every Python project to isolate its dependencies from the global Python installation and from other projects. This is a critical practice for preventing version conflicts and ensuring a reproducible environment.75

Best practices include:

* **Creation**: Create a virtual environment for each project, typically in a directory named .venv within the project root, using the command python \-m venv.venv.76  
* **Activation**: Activate the environment before installing dependencies or running the application. This ensures that the project uses its isolated set of packages.  
* **Version Control**: Add the virtual environment directory to your .gitignore file. It should never be committed to version control, as it contains machine-specific paths and can be very large.76  
* **Disposability**: Treat virtual environments as disposable. They should be easily and quickly recreated from a dependency file. Never manually modify files within the venv directory.76

#### **6.1.3. Dependency Management with pip and requirements.txt**

Project dependencies must be explicitly declared and pinned to specific versions to ensure deterministic and reproducible builds across all environments (development, testing, production).78

Best practices include:

* **Use requirements.txt**: This file should list all project dependencies. It is the standard way to declare dependencies for applications.79  
* **Pinning Versions**: Always pin exact versions (e.g., requests==2.28.1) rather than using ranges (requests\>=2.25.0). This prevents unexpected breaking changes when a dependency releases a new version.75  
* **Generating requirements.txt**: To ensure all direct and transitive (sub-dependencies) are captured, use pip freeze \> requirements.txt from within your activated virtual environment.79  
* **Advanced: pip-tools**: For more robust dependency management, use the pip-compile command from the pip-tools package. This allows you to maintain a requirements.in file with only your direct, high-level dependencies. pip-compile then generates a fully pinned requirements.txt file with all transitive dependencies resolved. This makes dependency updates more manageable while still ensuring deterministic builds.81

### **6.2. TypeScript Best Practices**

#### **6.2.1. Leveraging the Static Type System**

The primary benefit of TypeScript is its static type system. Using it to its full potential is critical for catching errors at compile time, improving code quality, and enhancing tooling and the overall developer experience.82

Best practices include:

* **Avoid any**: The any type opts out of type checking and negates the benefits of TypeScript. Avoid it whenever possible. For values whose type is truly unknown, use the unknown type, which is type-safe because it forces you to perform explicit type-checking before you can operate on the value.82  
* **Use Generics**: Create reusable and type-safe functions, classes, and components with generics. This allows you to write flexible code that can work over a variety of types while maintaining type safety.84  
* **Embrace Type Inference**: Allow TypeScript to infer types for variables and properties from their initial values to reduce boilerplate code (e.g., const name \= 'Alice'; is inferred as string). However, it is a best practice to be explicit with function parameters and return types to create clear and stable API boundaries.84  
* **Use Utility Types**: Leverage TypeScript's built-in utility types like Partial\<T\>, Readonly\<T\>, Pick\<T, K\>, and Omit\<T, K\> to transform existing types without writing repetitive boilerplate code.85

#### **6.2.2. Strict tsconfig.json Configuration**

A strict tsconfig.json configuration enables more thorough type-checking, catching a wider range of potential runtime errors during compilation. This is the most effective way to maximize the safety benefits of TypeScript.

Key settings to enable in compilerOptions:

* **"strict": true**: This is the most important setting. It enables a suite of strict type-checking options, including all of the following. It should be the default for all new projects.84  
* **"noImplicitAny": true**: Raises an error on expressions and declarations with an implied any type. This ensures that every variable has a known type.  
* **"strictNullChecks": true**: When enabled, null and undefined are no longer assignable to every type. This forces you to explicitly handle cases where a value could be null or undefined, preventing a large class of common runtime errors.  
* **"forceConsistentCasingInFileNames": true**: Ensures that case-sensitive file systems do not cause issues by enforcing consistent casing in module imports.

#### **6.2.3. interface vs. type**

Both interface and type can be used to define the shape of an object. Understanding their differences helps in choosing the right tool for the job and maintaining consistency.

* **Key Differences**:  
  * **Extensibility**: An interface can be extended using the extends keyword. It can also be "declaration merged," meaning if you define an interface with the same name twice in the same scope, their properties are merged. A type alias cannot be merged and is extended using intersection types (&).  
  * **Flexibility**: A type alias is more flexible; it can represent not only object shapes but also unions, intersections, tuples, primitives, and mapped types.  
* **Best Practices**:  
  * **Use interface for**: Defining the shape of objects or the contract for classes that will be implemented (implements). Their ability to be merged makes them particularly well-suited for augmenting types from external libraries via declaration merging.  
  * **Use type for**: Defining unions, intersections, tuples, or using utility types to create new types from existing ones. Use type when you need a definitive, non-extendable shape.  
  * **Consistency is Key**: The most important rule is to be consistent within a single codebase. Many teams establish a convention to prefer interface for object shapes and type for all other type definitions.

