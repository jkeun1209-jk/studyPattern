"""
GoF 23개 디자인 패턴 — Java Spring Boot 정적 데이터
레이어 구조: contract / application / domain / infra / presentation
각 패턴: overview, use_case, layers_used, flow_description, example_code, package_structure, key_benefits
"""

PATTERNS_DATA = {

    # ══════════════════════════════════════════════════
    # CREATIONAL PATTERNS (생성 패턴)
    # ══════════════════════════════════════════════════

    "Singleton": {
        "pattern_name": "Singleton",
        "category": "creational",
        "overview": "클래스의 인스턴스가 오직 하나만 생성되도록 보장하고 전역 접근점을 제공하는 패턴입니다. Spring Framework에서는 @Bean이 기본적으로 싱글턴 스코프로 관리됩니다.",
        "use_case": "애플리케이션 전역에서 공유되어야 하는 설정 관리자, 커넥션 풀, 캐시 매니저 등에 활용합니다. Spring IoC 컨테이너가 Bean을 싱글턴으로 관리하므로 @Service, @Repository는 자동으로 싱글턴이 됩니다.",
        "layers_used": ["domain", "infra"],
        "flow_description": [
            "① 클라이언트가 ApplicationConfigManager.getInstance()를 호출합니다.",
            "② 첫 번째 null 체크 — 인스턴스가 이미 있으면 동기화 없이 바로 반환합니다 (성능 최적화).",
            "③ 인스턴스가 없으면 synchronized 블록에 진입하여 스레드 경합을 차단합니다.",
            "④ 블록 진입 후 두 번째 null 체크(Double-Checked Locking)로 중복 생성을 방지합니다.",
            "⑤ AppBeanConfig의 @Bean 메서드는 Spring 컨테이너가 싱글턴으로 관리하므로 한 번만 호출됩니다.",
            "⑥ 이후 모든 주입 지점에서 동일한 인스턴스가 반환됩니다."
        ],
        "example_code": """\
// ===== [domain/ApplicationConfigManager.java] =====
package com.example.singleton.domain;

import java.util.HashMap;
import java.util.Map;

public class ApplicationConfigManager {

    // volatile: 캐시 없이 메인 메모리에서 직접 읽어 가시성 보장
    private static volatile ApplicationConfigManager instance;
    private final Map<String, String> configs = new HashMap<>();

    // private 생성자 — 외부에서 new로 생성 불가
    private ApplicationConfigManager() {
        configs.put("app.name", "Design Pattern PoC");
        configs.put("app.version", "1.0.0");
    }

    // Double-Checked Locking: 성능과 스레드 안전성을 동시에 확보
    public static ApplicationConfigManager getInstance() {
        if (instance == null) {                              // 1차 체크 (동기화 없이 빠르게 확인)
            synchronized (ApplicationConfigManager.class) { // 락 획득
                if (instance == null) {                      // 2차 체크 (락 안에서 중복 생성 방지)
                    instance = new ApplicationConfigManager();
                }
            }
        }
        return instance;
    }

    public String getConfig(String key) {
        return configs.getOrDefault(key, "");
    }

    public void setConfig(String key, String value) {
        configs.put(key, value);
    }
}

// ===== [infra/AppBeanConfig.java] =====
package com.example.singleton.infra;

import com.example.singleton.domain.ApplicationConfigManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class AppBeanConfig {

    // @Bean 기본 스코프 = singleton: Spring이 이 메서드를 한 번만 호출하고 결과를 재사용
    @Bean
    public ApplicationConfigManager applicationConfigManager() {
        return ApplicationConfigManager.getInstance();
    }
}""",
        "package_structure": """\
com.example.singleton
├── domain
│   └── ApplicationConfigManager.java
└── infra
    └── AppBeanConfig.java""",
        "key_benefits": [
            "하나의 인스턴스만 생성되어 메모리를 절약합니다",
            "전역 상태를 일관성 있게 관리할 수 있습니다",
            "Spring의 기본 Bean 관리 방식과 자연스럽게 일치합니다",
        ],
    },

    "Factory Method": {
        "pattern_name": "Factory Method",
        "category": "creational",
        "overview": "객체 생성을 위한 인터페이스를 정의하되, 어떤 클래스를 생성할지는 서브클래스가 결정하도록 위임하는 패턴입니다. 객체 생성 로직을 클라이언트 코드로부터 분리합니다.",
        "use_case": "알림 발송 채널(Email/SMS/Push)처럼 동일한 인터페이스를 구현하는 여러 구현체가 있고, 런타임에 어떤 구현체를 생성할지 결정해야 할 때 사용합니다. Spring의 @Qualifier와 함께 활용하면 효과적입니다.",
        "layers_used": ["contract", "domain", "application"],
        "flow_description": [
            "① 클라이언트(NotificationService)는 NotificationFactory 인터페이스만 알고 있습니다.",
            "② 런타임에 주입된 구체 팩토리(EmailNotificationFactory 등)가 결정됩니다.",
            "③ factory.create()가 호출되면 해당 팩토리가 적절한 NotificationSender 구현체를 반환합니다.",
            "④ 클라이언트는 sender.send()를 호출하며, 어떤 채널(Email/SMS)인지 알 필요가 없습니다.",
            "⑤ 새 채널 추가 시 NotificationSender 구현체와 Factory만 추가하면 됩니다 — 기존 코드 무변경."
        ],
        "example_code": """\
// ===== [contract/NotificationSender.java] =====
package com.example.factorymethod.contract;

// 모든 알림 발송 채널이 구현해야 하는 공통 인터페이스
public interface NotificationSender {
    void send(String recipient, String message);
    String getType(); // 채널 유형 식별자 (EMAIL, SMS 등)
}

// ===== [contract/NotificationFactory.java] =====
package com.example.factorymethod.contract;

// 팩토리 메서드 패턴의 핵심: 생성 메서드를 인터페이스로 정의
public interface NotificationFactory {
    NotificationSender create(); // 어떤 구현체를 만들지는 서브클래스가 결정
}

// ===== [domain/EmailNotification.java] =====
package com.example.factorymethod.domain;

import com.example.factorymethod.contract.NotificationSender;
import org.springframework.stereotype.Component;

@Component // Spring Bean으로 등록 — 의존성 주입 가능
public class EmailNotification implements NotificationSender {

    @Override
    public void send(String recipient, String message) {
        // 실제 이메일 발송 로직 (SMTP 등)
        System.out.printf("[EMAIL] %s → %s%n", recipient, message);
    }

    @Override
    public String getType() { return "EMAIL"; }
}

// ===== [domain/SmsNotification.java] =====
package com.example.factorymethod.domain;

import com.example.factorymethod.contract.NotificationSender;
import org.springframework.stereotype.Component;

@Component
public class SmsNotification implements NotificationSender {

    @Override
    public void send(String recipient, String message) {
        System.out.printf("[SMS] %s → %s%n", recipient, message);
    }

    @Override
    public String getType() { return "SMS"; }
}

// ===== [application/EmailNotificationFactory.java] =====
package com.example.factorymethod.application;

import com.example.factorymethod.contract.NotificationFactory;
import com.example.factorymethod.contract.NotificationSender;
import com.example.factorymethod.domain.EmailNotification;
import org.springframework.stereotype.Component;

@Component("emailFactory") // Bean 이름으로 특정 팩토리 선택 가능
public class EmailNotificationFactory implements NotificationFactory {

    private final EmailNotification emailNotification;

    public EmailNotificationFactory(EmailNotification emailNotification) {
        this.emailNotification = emailNotification;
    }

    @Override
    public NotificationSender create() {
        return emailNotification; // 이메일 발송 구현체 반환
    }
}

// ===== [application/NotificationService.java] =====
package com.example.factorymethod.application;

import com.example.factorymethod.contract.NotificationFactory;
import com.example.factorymethod.contract.NotificationSender;
import org.springframework.stereotype.Service;

@Service
public class NotificationService {

    // 구체 팩토리가 아닌 인터페이스에 의존 — 느슨한 결합
    private final NotificationFactory factory;

    public NotificationService(NotificationFactory factory) {
        this.factory = factory; // 생성자 주입으로 팩토리 교체 용이
    }

    public void notify(String recipient, String message) {
        NotificationSender sender = factory.create(); // 팩토리가 적절한 구현체 생성
        sender.send(recipient, message);              // 채널 종류와 무관하게 동일 인터페이스 사용
    }
}""",
        "package_structure": """\
com.example.factorymethod
├── contract
│   ├── NotificationFactory.java
│   └── NotificationSender.java
├── domain
│   ├── EmailNotification.java
│   └── SmsNotification.java
└── application
    ├── EmailNotificationFactory.java
    ├── SmsNotificationFactory.java
    └── NotificationService.java""",
        "key_benefits": [
            "객체 생성 코드와 비즈니스 로직을 분리하여 단일 책임 원칙을 지킵니다",
            "새로운 알림 채널 추가 시 기존 코드 변경 없이 확장이 가능합니다 (OCP)",
            "Spring 의존성 주입과 결합하면 런타임 전략 교체가 용이합니다",
        ],
    },

    "Abstract Factory": {
        "pattern_name": "Abstract Factory",
        "category": "creational",
        "overview": "서로 연관되거나 의존하는 객체들의 집합(제품군)을 생성하는 인터페이스를 제공하며, 구체적인 클래스를 명시하지 않는 패턴입니다.",
        "use_case": "클라우드 환경(AWS/GCP)에 따라 스토리지, 메시지큐 등 인프라 컴포넌트를 일관되게 교체해야 할 때 사용합니다. 환경별 인프라 빈 구성에 @Profile과 함께 활용하면 강력합니다.",
        "layers_used": ["contract", "infra"],
        "flow_description": [
            "① Spring 프로파일(@Profile)에 따라 AwsInfraFactory 또는 GcpInfraFactory가 활성화됩니다.",
            "② 비즈니스 로직은 CloudInfraFactory 인터페이스만 주입받아 사용합니다.",
            "③ factory.createStorage()를 호출하면 현재 프로파일에 맞는 스토리지 구현체가 반환됩니다.",
            "④ factory.createQueue()도 동일하게 같은 클라우드 환경의 구현체를 반환합니다.",
            "⑤ AWS → GCP 전환 시 spring.profiles.active 값만 변경하면 됩니다 — 비즈니스 코드 무변경."
        ],
        "example_code": """\
// ===== [contract/CloudStorage.java] =====
package com.example.abstractfactory.contract;

// 스토리지 제품군의 공통 인터페이스
public interface CloudStorage {
    void upload(String fileName, byte[] data);
    byte[] download(String fileName);
}

// ===== [contract/CloudQueue.java] =====
package com.example.abstractfactory.contract;

// 메시지 큐 제품군의 공통 인터페이스
public interface CloudQueue {
    void publish(String topic, String message);
    String consume(String topic);
}

// ===== [contract/CloudInfraFactory.java] =====
package com.example.abstractfactory.contract;

// 추상 팩토리: 연관된 제품군(스토리지 + 큐)을 함께 생성하는 인터페이스
public interface CloudInfraFactory {
    CloudStorage createStorage(); // 스토리지 구현체 생성
    CloudQueue   createQueue();   // 큐 구현체 생성
}

// ===== [infra/AwsS3Storage.java] =====
package com.example.abstractfactory.infra;

import com.example.abstractfactory.contract.CloudStorage;
import org.springframework.stereotype.Component;

@Component
public class AwsS3Storage implements CloudStorage {

    @Override
    public void upload(String fileName, byte[] data) {
        System.out.println("[AWS S3] 업로드: " + fileName); // 실제: AWS SDK 호출
    }

    @Override
    public byte[] download(String fileName) {
        System.out.println("[AWS S3] 다운로드: " + fileName);
        return new byte[0];
    }
}

// ===== [infra/AwsSqsQueue.java] =====
package com.example.abstractfactory.infra;

import com.example.abstractfactory.contract.CloudQueue;
import org.springframework.stereotype.Component;

@Component
public class AwsSqsQueue implements CloudQueue {

    @Override
    public void publish(String topic, String message) {
        System.out.println("[AWS SQS] 발행 → " + topic + ": " + message);
    }

    @Override
    public String consume(String topic) {
        return "[AWS SQS] 수신: " + topic;
    }
}

// ===== [infra/AwsInfraFactory.java] =====
package com.example.abstractfactory.infra;

import com.example.abstractfactory.contract.CloudInfraFactory;
import com.example.abstractfactory.contract.CloudStorage;
import com.example.abstractfactory.contract.CloudQueue;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

@Component
@Profile("aws") // spring.profiles.active=aws 일 때만 이 팩토리가 활성화됨
public class AwsInfraFactory implements CloudInfraFactory {

    // AWS 제품군을 함께 묶어 일관성 있게 제공
    private final AwsS3Storage s3Storage;
    private final AwsSqsQueue  sqsQueue;

    public AwsInfraFactory(AwsS3Storage s3Storage, AwsSqsQueue sqsQueue) {
        this.s3Storage = s3Storage;
        this.sqsQueue  = sqsQueue;
    }

    @Override public CloudStorage createStorage() { return s3Storage; } // AWS 스토리지 반환
    @Override public CloudQueue   createQueue()   { return sqsQueue; }  // AWS 큐 반환
}""",
        "package_structure": """\
com.example.abstractfactory
├── contract
│   ├── CloudInfraFactory.java
│   ├── CloudStorage.java
│   └── CloudQueue.java
└── infra
    ├── AwsS3Storage.java
    ├── AwsSqsQueue.java
    ├── AwsInfraFactory.java    ← @Profile("aws")
    ├── GcsStorage.java
    ├── GcsPubSubQueue.java
    └── GcpInfraFactory.java    ← @Profile("gcp")""",
        "key_benefits": [
            "인프라 제품군(AWS/GCP)을 코드 변경 없이 @Profile로 교체할 수 있습니다",
            "연관된 객체들의 일관성을 보장합니다 (AWS 스토리지 + AWS 큐)",
            "인프라 변경이 비즈니스 로직에 영향을 주지 않아 테스트가 용이합니다",
        ],
    },

    "Builder": {
        "pattern_name": "Builder",
        "category": "creational",
        "overview": "복잡한 객체의 생성 과정을 단계별로 분리하여, 동일한 생성 프로세스에서 다양한 표현을 만들 수 있게 하는 패턴입니다.",
        "use_case": "필드가 많은 도메인 객체(UserProfile, Order)나 선택적 매개변수가 많은 요청 DTO를 생성할 때 사용합니다. Lombok의 @Builder 어노테이션으로 간편하게 적용할 수 있습니다.",
        "layers_used": ["domain", "presentation"],
        "flow_description": [
            "① UserProfile.builder(필수값)으로 Builder 인스턴스를 생성합니다 (필수 필드 강제).",
            "② .phoneNumber(), .address() 등 선택 메서드를 체이닝 방식으로 호출합니다.",
            "③ 각 메서드는 Builder 자신을 반환하므로 연속 호출(Fluent API)이 가능합니다.",
            "④ .build()를 호출하면 Builder가 UserProfile 생성자에 모든 필드를 전달하고 불변 객체를 생성합니다.",
            "⑤ CreateUserRequest는 Lombok @Builder로 동일 패턴을 자동 적용한 DTO 예시입니다."
        ],
        "example_code": """\
// ===== [domain/UserProfile.java] =====
package com.example.builder.domain;

// 불변(Immutable) 도메인 객체 — 생성 후 수정 불가
public class UserProfile {

    // final 필드: 생성 후 변경 불가
    private final String  username;
    private final String  email;
    private final String  phoneNumber;
    private final String  address;
    private final int     age;
    private final boolean emailVerified;

    // private 생성자: Builder를 통해서만 생성 가능
    private UserProfile(Builder builder) {
        this.username      = builder.username;
        this.email         = builder.email;
        this.phoneNumber   = builder.phoneNumber;
        this.address       = builder.address;
        this.age           = builder.age;
        this.emailVerified = builder.emailVerified;
    }

    public String  getUsername()      { return username; }
    public String  getEmail()         { return email; }
    public String  getPhoneNumber()   { return phoneNumber; }
    public String  getAddress()       { return address; }
    public int     getAge()           { return age; }
    public boolean isEmailVerified()  { return emailVerified; }

    // 빌더 진입점: 필수 필드(username, email)를 강제로 받음
    public static Builder builder(String username, String email) {
        return new Builder(username, email);
    }

    public static class Builder {
        // 필수 필드 — null 허용 안 함
        private final String username;
        private final String email;

        // 선택 필드 — 기본값 설정
        private String  phoneNumber   = "";
        private String  address       = "";
        private int     age           = 0;
        private boolean emailVerified = false;

        public Builder(String username, String email) {
            this.username = username;
            this.email    = email;
        }

        // 체이닝 지원: 각 setter가 Builder 자신을 반환
        public Builder phoneNumber(String v) { this.phoneNumber   = v; return this; }
        public Builder address(String v)     { this.address       = v; return this; }
        public Builder age(int v)            { this.age           = v; return this; }
        public Builder emailVerified(boolean v) { this.emailVerified = v; return this; }

        // 최종 객체 생성
        public UserProfile build() { return new UserProfile(this); }
    }
}

// ===== [presentation/CreateUserRequest.java] =====
package com.example.builder.presentation;

import com.example.builder.domain.UserProfile;
import lombok.Builder;
import lombok.Getter;

// Lombok @Builder: Builder 내부 클래스 및 체이닝 메서드를 자동 생성
@Getter
@Builder
public class CreateUserRequest {

    private String  username;
    private String  email;
    private String  phoneNumber;
    private String  address;
    private int     age;

    // 요청 DTO → 도메인 객체 변환
    public UserProfile toDomain() {
        return UserProfile.builder(username, email)
                .phoneNumber(phoneNumber)
                .address(address)
                .age(age)
                .build();
    }
}""",
        "package_structure": """\
com.example.builder
├── domain
│   └── UserProfile.java
└── presentation
    └── CreateUserRequest.java""",
        "key_benefits": [
            "필드가 많아도 가독성 있게 객체를 생성할 수 있습니다",
            "필수/선택 필드를 명확히 구분하고 불변 객체를 만들 수 있습니다",
            "Lombok @Builder로 보일러플레이트 코드를 제거할 수 있습니다",
        ],
    },

    "Prototype": {
        "pattern_name": "Prototype",
        "category": "creational",
        "overview": "기존 객체를 복사(clone)하여 새 객체를 생성하는 패턴입니다. 객체 생성 비용이 클 때, 새로 생성하는 것보다 복사가 효율적인 경우에 사용합니다.",
        "use_case": "보고서 템플릿, 이메일 템플릿처럼 기본 구조가 동일하고 일부만 변경하는 객체를 반복 생성해야 할 때 사용합니다. Spring에서는 @Scope(\"prototype\")으로 매 요청마다 새 인스턴스를 생성합니다.",
        "layers_used": ["contract", "domain"],
        "flow_description": [
            "① TemplateRegistry에 미리 만들어진 원본 템플릿(welcome, password 등)이 등록됩니다.",
            "② 클라이언트가 getTemplate(\"welcome\")을 호출합니다.",
            "③ Registry는 원본을 직접 반환하지 않고 original.clone()으로 복사본을 생성합니다.",
            "④ EmailTemplate의 복사 생성자가 호출되어 모든 필드를 깊은 복사(Deep Copy)합니다.",
            "⑤ 클라이언트는 복사본의 내용을 자유롭게 수정해도 원본에 영향을 주지 않습니다."
        ],
        "example_code": """\
// ===== [contract/DocumentTemplate.java] =====
package com.example.prototype.contract;

// 복제 가능 객체의 인터페이스 — clone() 메서드 강제
public interface DocumentTemplate {
    DocumentTemplate clone(); // 자기 자신의 복사본 반환
    void setTitle(String title);
    void setContent(String content);
    String render();
}

// ===== [domain/EmailTemplate.java] =====
package com.example.prototype.domain;

import com.example.prototype.contract.DocumentTemplate;

public class EmailTemplate implements DocumentTemplate {

    private String title;
    private String content;
    private String footer; // 변경되지 않는 공통 푸터

    // 원본 생성 생성자
    public EmailTemplate(String title, String content, String footer) {
        this.title   = title;
        this.content = content;
        this.footer  = footer;
    }

    // 깊은 복사(Deep Copy) 생성자 — 모든 필드를 독립적으로 복사
    private EmailTemplate(EmailTemplate source) {
        this.title   = source.title;
        this.content = source.content;
        this.footer  = source.footer;
    }

    @Override
    public DocumentTemplate clone() {
        return new EmailTemplate(this); // 복사 생성자를 통해 독립된 객체 생성
    }

    @Override
    public void setTitle(String title)     { this.title = title; }

    @Override
    public void setContent(String content) { this.content = content; }

    @Override
    public String render() {
        return "제목: " + title + "\\n내용: " + content + "\\n---\\n" + footer;
    }
}

// ===== [domain/TemplateRegistry.java] =====
package com.example.prototype.domain;

import com.example.prototype.contract.DocumentTemplate;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Component
public class TemplateRegistry {

    // 원본 템플릿 풀 — 절대 직접 반환하지 않음
    private final Map<String, DocumentTemplate> templates = new HashMap<>();

    public TemplateRegistry() {
        // 애플리케이션 시작 시 원본 템플릿 등록
        templates.put("welcome",  new EmailTemplate("환영합니다", "서비스에 가입해 주셔서 감사합니다.", "문의: support@example.com"));
        templates.put("password", new EmailTemplate("비밀번호 변경", "비밀번호가 변경되었습니다.", "문의: support@example.com"));
    }

    // 항상 복사본을 반환 — 원본 보호
    public DocumentTemplate getTemplate(String name) {
        DocumentTemplate original = templates.get(name);
        if (original == null) throw new IllegalArgumentException("템플릿 없음: " + name);
        return original.clone(); // 원본이 아닌 복제본 반환
    }
}""",
        "package_structure": """\
com.example.prototype
├── contract
│   └── DocumentTemplate.java
└── domain
    ├── EmailTemplate.java
    └── TemplateRegistry.java""",
        "key_benefits": [
            "복잡한 객체를 매번 새로 생성하는 비용을 줄입니다",
            "원본 객체를 보호하면서 복사본을 자유롭게 수정할 수 있습니다",
            "Spring @Scope(\"prototype\")과 결합하면 Bean 단위로 프로토타입을 관리할 수 있습니다",
        ],
    },

    # ══════════════════════════════════════════════════
    # STRUCTURAL PATTERNS (구조 패턴)
    # ══════════════════════════════════════════════════

    "Adapter": {
        "pattern_name": "Adapter",
        "category": "structural",
        "overview": "호환되지 않는 인터페이스를 가진 클래스들이 함께 동작할 수 있도록 중간에 변환 역할을 하는 패턴입니다. 기존 코드를 수정하지 않고 새 인터페이스에 맞게 변환합니다.",
        "use_case": "레거시 결제 시스템이나 외부 서드파티 API를 내부 인터페이스에 맞게 연결할 때 사용합니다. infra 레이어에서 외부 시스템을 내부 contract에 맞게 어댑팅하는 것이 일반적인 패턴입니다.",
        "layers_used": ["contract", "infra"],
        "flow_description": [
            "① 비즈니스 로직은 PaymentProcessor 인터페이스만 알고 있습니다.",
            "② LegacyPaymentAdapter가 PaymentProcessor를 구현하고 @Component로 등록됩니다.",
            "③ processPayment() 호출 시 어댑터가 새 인터페이스의 파라미터(String orderId, double amount)를 레거시 형식(long, int)으로 변환합니다.",
            "④ 변환된 값으로 LegacyPaymentSystem.executePayment()를 호출합니다.",
            "⑤ 레거시 결과(int 코드)를 새 인터페이스의 반환 타입(boolean)으로 변환하여 반환합니다."
        ],
        "example_code": """\
// ===== [contract/PaymentProcessor.java] =====
package com.example.adapter.contract;

// 비즈니스 로직이 의존하는 내부 표준 인터페이스
public interface PaymentProcessor {
    boolean processPayment(String orderId, double amount, String currency);
    String  getTransactionId(String orderId);
}

// ===== [infra/LegacyPaymentSystem.java] =====
package com.example.adapter.infra;

// 레거시 외부 시스템 — 수정 불가, 다른 타입/네이밍 규칙 사용
public class LegacyPaymentSystem {

    // 레거시 API: 주문번호(long), 금액(센트 단위 int) 사용
    public int executePayment(long orderNumber, int amountInCents) {
        System.out.printf("[Legacy] 결제 처리 - 주문: %d, 금액: %d원%n", orderNumber, amountInCents);
        return 200; // 레거시 성공 코드 (HTTP와 유사)
    }

    public String getPaymentKey(long orderNumber) {
        return "LEGACY-TXN-" + orderNumber;
    }
}

// ===== [infra/LegacyPaymentAdapter.java] =====
package com.example.adapter.infra;

import com.example.adapter.contract.PaymentProcessor;
import org.springframework.stereotype.Component;

// 어댑터: 새 인터페이스(PaymentProcessor)와 레거시 시스템 사이의 변환 담당
@Component
public class LegacyPaymentAdapter implements PaymentProcessor {

    private final LegacyPaymentSystem legacySystem;

    public LegacyPaymentAdapter() {
        this.legacySystem = new LegacyPaymentSystem();
    }

    @Override
    public boolean processPayment(String orderId, double amount, String currency) {
        // 새 인터페이스 타입 → 레거시 타입으로 변환
        long orderNumber   = Long.parseLong(orderId.replaceAll("\\\\D", "")); // String → long
        int  amountInCents = (int)(amount * 100);                              // double(원) → int(센트)

        int resultCode = legacySystem.executePayment(orderNumber, amountInCents);
        return resultCode == 200; // 레거시 결과 코드 → boolean으로 변환
    }

    @Override
    public String getTransactionId(String orderId) {
        long orderNumber = Long.parseLong(orderId.replaceAll("\\\\D", ""));
        return legacySystem.getPaymentKey(orderNumber); // 레거시 키 형식을 그대로 반환
    }
}""",
        "package_structure": """\
com.example.adapter
├── contract
│   └── PaymentProcessor.java
└── infra
    ├── LegacyPaymentSystem.java   ← 수정 불가 레거시
    └── LegacyPaymentAdapter.java  ← 어댑터 (변환 담당)""",
        "key_benefits": [
            "레거시 코드를 수정하지 않고 새 인터페이스에 통합할 수 있습니다",
            "외부 시스템 변경 시 어댑터만 교체하면 되므로 영향 범위가 최소화됩니다",
            "단일 책임 원칙(SRP)을 지키면서 인터페이스 변환 책임을 분리합니다",
        ],
    },

    "Bridge": {
        "pattern_name": "Bridge",
        "category": "structural",
        "overview": "추상화(Abstraction)와 구현(Implementation)을 분리하여 독립적으로 변경할 수 있게 하는 패턴입니다. 두 계층이 각각 확장될 수 있습니다.",
        "use_case": "메시지 유형(일반/긴급)과 발송 채널(이메일/SMS)이 독립적으로 확장되어야 할 때 사용합니다. N×M 조합을 상속으로 처리하면 클래스가 폭발적으로 늘어나는 문제를 브릿지로 해결합니다.",
        "layers_used": ["contract", "domain", "infra"],
        "flow_description": [
            "① Message(추상화)는 생성 시 MessageChannel(구현부)을 브릿지로 주입받습니다.",
            "② RegularMessage 또는 UrgentMessage 중 하나를 선택합니다 (메시지 유형 결정).",
            "③ EmailChannel 또는 SmsChannel 중 하나를 주입합니다 (발송 채널 결정).",
            "④ message.send()가 호출되면 추상화 계층(메시지 유형)이 제목 포맷을 결정합니다.",
            "⑤ 내부적으로 channel.deliver()를 호출하여 실제 발송을 구현 계층에 위임합니다.",
            "⑥ 2×2=4가지 조합이 클래스 2+2개로 해결됩니다 (N+M, 상속이면 N×M 필요)."
        ],
        "example_code": """\
// ===== [contract/MessageChannel.java] =====
package com.example.bridge.contract;

// 구현부(Implementation) 인터페이스: 실제 발송 방법을 정의
public interface MessageChannel {
    void deliver(String recipient, String subject, String body);
}

// ===== [domain/Message.java] =====
package com.example.bridge.domain;

import com.example.bridge.contract.MessageChannel;

// 추상화(Abstraction) 계층: 메시지 유형을 정의, 채널은 브릿지로 연결
public abstract class Message {

    // 브릿지: 추상화가 구현부를 참조 (합성, 상속 아님)
    protected final MessageChannel channel;

    protected Message(MessageChannel channel) {
        this.channel = channel; // 런타임에 어떤 채널이든 주입 가능
    }

    public abstract void send(String recipient, String content);
}

// ===== [domain/RegularMessage.java] =====
package com.example.bridge.domain;

import com.example.bridge.contract.MessageChannel;

// 구체 추상화: 일반 메시지 — 제목 포맷만 다름
public class RegularMessage extends Message {

    public RegularMessage(MessageChannel channel) { super(channel); }

    @Override
    public void send(String recipient, String content) {
        channel.deliver(recipient, "[일반]", content); // 채널에 발송 위임
    }
}

// ===== [domain/UrgentMessage.java] =====
package com.example.bridge.domain;

import com.example.bridge.contract.MessageChannel;

// 구체 추상화: 긴급 메시지 — 제목에 긴급 표시
public class UrgentMessage extends Message {

    public UrgentMessage(MessageChannel channel) { super(channel); }

    @Override
    public void send(String recipient, String content) {
        channel.deliver(recipient, "[긴급!]", content); // 동일 채널, 다른 포맷
    }
}

// ===== [infra/EmailChannel.java] =====
package com.example.bridge.infra;

import com.example.bridge.contract.MessageChannel;
import org.springframework.stereotype.Component;

@Component("emailChannel") // Bean 이름으로 특정 채널 선택 가능
public class EmailChannel implements MessageChannel {

    @Override
    public void deliver(String recipient, String subject, String body) {
        // 실제: JavaMail, SendGrid 등 이메일 발송 라이브러리 호출
        System.out.printf("[EMAIL] To: %s | %s %s%n", recipient, subject, body);
    }
}

// ===== [infra/SmsChannel.java] =====
package com.example.bridge.infra;

import com.example.bridge.contract.MessageChannel;
import org.springframework.stereotype.Component;

@Component("smsChannel")
public class SmsChannel implements MessageChannel {

    @Override
    public void deliver(String recipient, String subject, String body) {
        // 실제: Twilio, NCP SMS 등 API 호출
        System.out.printf("[SMS] To: %s | %s%s%n", recipient, subject, body);
    }
}""",
        "package_structure": """\
com.example.bridge
├── contract
│   └── MessageChannel.java     ← 구현부 인터페이스
├── domain
│   ├── Message.java            ← 추상화 (브릿지 보유)
│   ├── RegularMessage.java
│   └── UrgentMessage.java
└── infra
    ├── EmailChannel.java        ← 구현체
    └── SmsChannel.java""",
        "key_benefits": [
            "메시지 유형과 채널을 독립적으로 확장하여 N×M 클래스 폭발을 방지합니다",
            "런타임에 채널을 교체하는 유연성을 제공합니다",
            "추상화와 구현이 분리되어 단위 테스트가 쉬워집니다",
        ],
    },

    "Composite": {
        "pattern_name": "Composite",
        "category": "structural",
        "overview": "개별 객체와 복합 객체를 동일한 인터페이스로 처리할 수 있게 하여 트리 구조를 표현하는 패턴입니다. 클라이언트는 단일 객체와 복합 객체를 구분하지 않고 다룹니다.",
        "use_case": "카테고리 트리, 메뉴 구조, 조직도처럼 계층적 구조를 표현해야 할 때 사용합니다. Spring의 ApplicationContext 자체도 빈들을 계층적으로 관리하는 컴포짓 구조입니다.",
        "layers_used": ["contract", "domain"],
        "flow_description": [
            "① Category(복합 노드)와 Product(단말 노드) 모두 CategoryComponent 인터페이스를 구현합니다.",
            "② 클라이언트는 최상위 Category에 add()로 하위 Category나 Product를 추가합니다.",
            "③ print()가 호출되면 Category는 자신을 출력 후 모든 자식에게 재귀적으로 print()를 위임합니다.",
            "④ Product(Leaf)는 자식이 없으므로 재귀가 멈추고 자신만 출력합니다.",
            "⑤ 클라이언트 코드는 Category인지 Product인지 구별 없이 동일하게 print()를 호출합니다."
        ],
        "example_code": """\
// ===== [contract/CategoryComponent.java] =====
package com.example.composite.contract;

import java.util.List;

// Leaf(단말)와 Composite(복합) 모두가 구현하는 단일 인터페이스
public interface CategoryComponent {
    String getName();
    void   add(CategoryComponent component);    // Leaf에서는 UnsupportedOperationException
    void   remove(CategoryComponent component);
    List<CategoryComponent> getChildren();
    void   print(String indent);               // 재귀 출력
}

// ===== [domain/Category.java] =====
package com.example.composite.domain;

import com.example.composite.contract.CategoryComponent;
import java.util.ArrayList;
import java.util.List;

// Composite: 자식을 가질 수 있는 복합 노드
public class Category implements CategoryComponent {

    private final String name;
    private final List<CategoryComponent> children = new ArrayList<>(); // 자식 목록

    public Category(String name) { this.name = name; }

    @Override public String getName() { return name; }

    @Override
    public void add(CategoryComponent c) { children.add(c); } // 자식 추가

    @Override
    public void remove(CategoryComponent c) { children.remove(c); }

    @Override
    public List<CategoryComponent> getChildren() { return children; }

    @Override
    public void print(String indent) {
        System.out.println(indent + "📁 " + name);               // 자신 출력
        children.forEach(c -> c.print(indent + "  ")); // 자식에게 재귀 위임
    }
}

// ===== [domain/Product.java] =====
package com.example.composite.domain;

import com.example.composite.contract.CategoryComponent;
import java.util.Collections;
import java.util.List;

// Leaf: 자식을 가질 수 없는 단말 노드
public class Product implements CategoryComponent {

    private final String name;

    public Product(String name) { this.name = name; }

    @Override public String getName() { return name; }

    // Leaf는 자식 추가 불가 — 명시적 예외 발생
    @Override public void add(CategoryComponent c) { throw new UnsupportedOperationException("상품은 자식을 가질 수 없습니다"); }
    @Override public void remove(CategoryComponent c) { throw new UnsupportedOperationException(); }
    @Override public List<CategoryComponent> getChildren() { return Collections.emptyList(); }

    @Override
    public void print(String indent) {
        System.out.println(indent + "📄 " + name); // 자신만 출력, 재귀 없음
    }
}""",
        "package_structure": """\
com.example.composite
├── contract
│   └── CategoryComponent.java
└── domain
    ├── Category.java   ← Composite (자식 보유 가능)
    └── Product.java    ← Leaf (단말 노드)""",
        "key_benefits": [
            "트리 구조를 단일 인터페이스로 균일하게 처리할 수 있습니다",
            "새로운 컴포넌트 추가 시 클라이언트 코드를 변경할 필요가 없습니다",
            "재귀적 탐색 구현이 간단해집니다",
        ],
    },

    "Decorator": {
        "pattern_name": "Decorator",
        "category": "structural",
        "overview": "객체에 동적으로 새로운 책임을 추가하는 패턴입니다. 서브클래싱 없이 기능을 확장할 수 있으며, 래퍼(Wrapper) 패턴이라고도 합니다.",
        "use_case": "주문 서비스에 로깅, 캐싱, 검증을 동적으로 추가할 때 사용합니다. Spring AOP(@Around)가 이 패턴의 대표적인 구현이며, HttpServletRequestWrapper도 데코레이터 패턴입니다.",
        "layers_used": ["contract", "application"],
        "flow_description": [
            "① ValidationOrderDecorator → LoggingOrderDecorator → BasicOrderService 순으로 체인이 구성됩니다.",
            "② createOrder() 호출 시 가장 바깥쪽 ValidationOrderDecorator가 먼저 입력값을 검증합니다.",
            "③ 검증 통과 후 delegate.createOrder()로 다음 레이어(LoggingOrderDecorator)에 위임합니다.",
            "④ 로깅 데코레이터가 호출 전 로그를 남기고, delegate.createOrder()로 실제 서비스에 위임합니다.",
            "⑤ BasicOrderService가 실제 주문을 처리하고 결과를 반환합니다.",
            "⑥ 반환값이 역순으로 전달되며 각 데코레이터가 후처리(로그 등)를 수행합니다."
        ],
        "example_code": """\
// ===== [contract/OrderService.java] =====
package com.example.decorator.contract;

import java.util.List;

// 기본 서비스와 모든 데코레이터가 구현하는 공통 인터페이스
public interface OrderService {
    String       createOrder(String productId, int quantity);
    List<String> getOrders(String customerId);
}

// ===== [application/BasicOrderService.java] =====
package com.example.decorator.application;

import com.example.decorator.contract.OrderService;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

// 핵심 비즈니스 로직만 담당 (로깅/검증 없음)
@Service
public class BasicOrderService implements OrderService {

    @Override
    public String createOrder(String productId, int quantity) {
        String orderId = UUID.randomUUID().toString();
        System.out.printf("[주문 생성] 상품: %s, 수량: %d → 주문ID: %s%n", productId, quantity, orderId);
        return orderId;
    }

    @Override
    public List<String> getOrders(String customerId) {
        return List.of("ORDER-001", "ORDER-002"); // 실제: DB 조회
    }
}

// ===== [application/LoggingOrderDecorator.java] =====
package com.example.decorator.application;

import com.example.decorator.contract.OrderService;
import java.util.List;

// 로깅 데코레이터: 실제 서비스를 감싸서 로그 기능 추가
public class LoggingOrderDecorator implements OrderService {

    private final OrderService delegate; // 감쌀 대상 (다음 레이어)

    public LoggingOrderDecorator(OrderService delegate) {
        this.delegate = delegate;
    }

    @Override
    public String createOrder(String productId, int quantity) {
        System.out.println("[LOG] createOrder 호출 - 상품: " + productId);       // 전처리: 호출 전 로그
        String result = delegate.createOrder(productId, quantity);               // 다음 레이어에 위임
        System.out.println("[LOG] createOrder 완료 - 주문ID: " + result);        // 후처리: 완료 후 로그
        return result;
    }

    @Override
    public List<String> getOrders(String customerId) {
        System.out.println("[LOG] getOrders 호출 - 고객: " + customerId);
        return delegate.getOrders(customerId);
    }
}

// ===== [application/ValidationOrderDecorator.java] =====
package com.example.decorator.application;

import com.example.decorator.contract.OrderService;
import java.util.List;

// 검증 데코레이터: 비즈니스 규칙 검증을 분리하여 추가
public class ValidationOrderDecorator implements OrderService {

    private final OrderService delegate;

    public ValidationOrderDecorator(OrderService delegate) {
        this.delegate = delegate;
    }

    @Override
    public String createOrder(String productId, int quantity) {
        // 검증 실패 시 예외 발생 — delegate는 호출되지 않음
        if (productId == null || productId.isBlank())
            throw new IllegalArgumentException("상품 ID는 필수입니다");
        if (quantity <= 0)
            throw new IllegalArgumentException("수량은 1 이상이어야 합니다");

        return delegate.createOrder(productId, quantity); // 검증 통과 후 위임
    }

    @Override
    public List<String> getOrders(String customerId) {
        if (customerId == null || customerId.isBlank())
            throw new IllegalArgumentException("고객 ID는 필수입니다");
        return delegate.getOrders(customerId);
    }
}""",
        "package_structure": """\
com.example.decorator
├── contract
│   └── OrderService.java
└── application
    ├── BasicOrderService.java          ← 핵심 로직
    ├── LoggingOrderDecorator.java      ← 로깅 추가
    └── ValidationOrderDecorator.java   ← 검증 추가""",
        "key_benefits": [
            "서브클래싱 없이 런타임에 기능을 동적으로 조합하고 추가할 수 있습니다",
            "단일 책임 원칙(SRP): 로깅, 검증 등 각 관심사를 별도 클래스로 분리합니다",
            "Spring AOP의 동작 원리와 동일하여 AOP 이해에 도움이 됩니다",
        ],
    },

    "Facade": {
        "pattern_name": "Facade",
        "category": "structural",
        "overview": "복잡한 서브시스템에 대한 단순화된 인터페이스를 제공하는 패턴입니다. 클라이언트가 여러 서브시스템을 직접 다루지 않고 파사드를 통해 접근합니다.",
        "use_case": "주문 처리처럼 재고 확인, 결제, 배송 등 여러 서비스를 조합해야 하는 복잡한 비즈니스 로직을 하나의 파사드로 단순화할 때 사용합니다. Controller → Facade → Service 구조가 대표적입니다.",
        "layers_used": ["application", "presentation"],
        "flow_description": [
            "① OrderController는 복잡한 서비스들을 직접 알지 않고, OrderFacade 하나만 의존합니다.",
            "② 주문 요청이 오면 OrderFacade.placeOrder()가 단일 진입점으로 호출됩니다.",
            "③ 파사드 내부에서 재고 확인 → 결제 처리 → 재고 차감 → 배송 생성 순서로 서브시스템을 호출합니다.",
            "④ 각 단계에서 실패 시 파사드가 예외를 처리하며 Controller에는 단순한 결과만 반환합니다.",
            "⑤ Controller는 전체 흐름을 알 필요 없이 orderId 결과만 받아 응답합니다."
        ],
        "example_code": """\
// ===== [application/InventoryService.java] =====
package com.example.facade.application;

import org.springframework.stereotype.Service;

// 서브시스템 1: 재고 관리 (복잡한 내부 로직 보유)
@Service
public class InventoryService {

    public boolean checkStock(String productId, int quantity) {
        System.out.println("[재고] 확인: " + productId + " × " + quantity);
        return true; // 실제: DB에서 재고 수량 조회
    }

    public void decreaseStock(String productId, int quantity) {
        System.out.println("[재고] 차감: " + productId + " × " + quantity);
    }
}

// ===== [application/PaymentService.java] =====
package com.example.facade.application;

import org.springframework.stereotype.Service;

// 서브시스템 2: 결제 처리 (PG사 연동 등 복잡한 로직)
@Service
public class PaymentService {

    public String processPayment(String customerId, double amount) {
        System.out.printf("[결제] 고객: %s, 금액: %.0f원%n", customerId, amount);
        return "TXN-" + System.currentTimeMillis(); // 거래 ID 반환
    }
}

// ===== [application/ShippingService.java] =====
package com.example.facade.application;

import org.springframework.stereotype.Service;

// 서브시스템 3: 배송 처리
@Service
public class ShippingService {

    public String createShipment(String orderId, String address) {
        System.out.printf("[배송] 주문: %s → %s%n", orderId, address);
        return "SHIP-" + orderId;
    }
}

// ===== [application/OrderFacade.java] =====
package com.example.facade.application;

import org.springframework.stereotype.Service;

// 파사드: 복잡한 3개 서브시스템을 하나의 단순한 메서드로 통합
@Service
public class OrderFacade {

    private final InventoryService inventoryService;
    private final PaymentService   paymentService;
    private final ShippingService  shippingService;

    public OrderFacade(InventoryService inventoryService,
                       PaymentService paymentService,
                       ShippingService shippingService) {
        this.inventoryService = inventoryService;
        this.paymentService   = paymentService;
        this.shippingService  = shippingService;
    }

    // 단일 진입점: 여러 서브시스템의 복잡한 협력을 하나의 메서드로 감춤
    public String placeOrder(String customerId, String productId,
                             int quantity, double price, String address) {
        // 1단계: 재고 확인
        if (!inventoryService.checkStock(productId, quantity)) {
            throw new IllegalStateException("재고 부족: " + productId);
        }
        // 2단계: 결제
        String txnId = paymentService.processPayment(customerId, price * quantity);

        // 3단계: 재고 차감 (결제 성공 후)
        inventoryService.decreaseStock(productId, quantity);

        // 4단계: 배송 생성
        String orderId    = "ORD-" + System.currentTimeMillis();
        String shipmentId = shippingService.createShipment(orderId, address);

        System.out.printf("[주문 완료] 주문: %s, 배송: %s, 결제: %s%n", orderId, shipmentId, txnId);
        return orderId;
    }
}

// ===== [presentation/OrderController.java] =====
package com.example.facade.presentation;

import com.example.facade.application.OrderFacade;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

// Controller는 OrderFacade만 의존 — 서브시스템 3개를 직접 알 필요 없음
@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderFacade orderFacade;

    public OrderController(OrderFacade orderFacade) {
        this.orderFacade = orderFacade;
    }

    @PostMapping
    public ResponseEntity<String> placeOrder(@RequestBody OrderRequest request) {
        // 파사드 호출 한 줄로 복잡한 주문 처리 완료
        String orderId = orderFacade.placeOrder(
            request.getCustomerId(), request.getProductId(),
            request.getQuantity(), request.getPrice(), request.getAddress()
        );
        return ResponseEntity.ok(orderId);
    }
}""",
        "package_structure": """\
com.example.facade
├── application
│   ├── InventoryService.java
│   ├── PaymentService.java
│   ├── ShippingService.java
│   └── OrderFacade.java       ← 파사드 (단일 진입점)
└── presentation
    └── OrderController.java""",
        "key_benefits": [
            "복잡한 서브시스템을 단일 진입점으로 단순화하여 클라이언트 코드를 깔끔하게 만듭니다",
            "Controller가 여러 서비스를 직접 의존하지 않아 결합도가 낮아집니다",
            "레이어 간 책임 분리가 명확해져 유지보수가 용이합니다",
        ],
    },

    "Flyweight": {
        "pattern_name": "Flyweight",
        "category": "structural",
        "overview": "많은 수의 유사한 객체를 효율적으로 공유하여 메모리 사용량을 줄이는 패턴입니다. 공유 가능한 내부 상태(Intrinsic)와 객체별 외부 상태(Extrinsic)를 분리합니다.",
        "use_case": "상품 카탈로그에서 동일한 카테고리 아이콘, 폰트 객체 등 많은 객체가 동일한 상태를 공유해야 할 때 사용합니다. Spring의 Bean 싱글턴 관리도 플라이웨이트 개념을 활용합니다.",
        "layers_used": ["domain", "infra"],
        "flow_description": [
            "① ProductIconFactory.getIcon(type, color)가 호출됩니다.",
            "② 캐시(iconPool)에 해당 key(type-color)가 존재하는지 확인합니다.",
            "③ 존재하면 기존 ProductIcon 객체를 즉시 반환합니다 (생성 비용 없음).",
            "④ 존재하지 않으면 새 ProductIcon을 생성(이미지 로드 등 무거운 작업 수행)하고 캐시에 저장합니다.",
            "⑤ 클라이언트는 반환받은 아이콘에 render(x, y, scale)을 호출하며, x/y/scale은 외부 상태로 매번 전달합니다.",
            "⑥ 1000개 상품이 같은 카테고리 아이콘을 공유하더라도 객체는 1개만 존재합니다."
        ],
        "example_code": """\
// ===== [domain/ProductIcon.java] =====
package com.example.flyweight.domain;

// Flyweight: 공유되는 내부 상태(Intrinsic State)만 보유
public class ProductIcon {

    // 내부 상태 (Intrinsic): 공유 가능, 변경 불가
    private final String iconType;   // 아이콘 유형 (e.g., "ELECTRONICS")
    private final String colorCode;  // 색상 코드 (e.g., "#FF0000")
    private final byte[] imageData;  // 무거운 이미지 데이터 (공유됨)

    public ProductIcon(String iconType, String colorCode) {
        this.iconType  = iconType;
        this.colorCode = colorCode;
        this.imageData = loadImage(iconType); // 생성 시 한 번만 로드
        System.out.println("[아이콘 생성] " + iconType + " (" + colorCode + ")");
    }

    // 외부 상태(Extrinsic State)는 파라미터로 전달 — 객체에 저장하지 않음
    public void render(int x, int y, double scale) {
        System.out.printf("[렌더링] %s at (%d,%d) scale=%.1f%n", iconType, x, y, scale);
        // 실제: imageData를 x,y 위치에 scale 크기로 그리기
    }

    private byte[] loadImage(String iconType) {
        return new byte[1024]; // 실제: 파일/리소스에서 이미지 로드
    }

    public String getIconType() { return iconType; }
}

// ===== [infra/ProductIconFactory.java] =====
package com.example.flyweight.infra;

import com.example.flyweight.domain.ProductIcon;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

// Flyweight Factory: 객체 풀 관리 — 기존 객체 재사용, 없으면 생성
@Component
public class ProductIconFactory {

    // 플라이웨이트 풀: key = "iconType-colorCode"
    private final Map<String, ProductIcon> iconPool = new HashMap<>();

    public ProductIcon getIcon(String iconType, String colorCode) {
        String key = iconType + "-" + colorCode;

        // computeIfAbsent: 키가 없을 때만 생성 함수 실행 (있으면 기존 반환)
        return iconPool.computeIfAbsent(key,
            k -> new ProductIcon(iconType, colorCode) // 없을 때만 생성
        );
    }

    public int getPoolSize() { return iconPool.size(); } // 실제 생성된 객체 수 확인용
}""",
        "package_structure": """\
com.example.flyweight
├── domain
│   └── ProductIcon.java        ← Flyweight (공유 객체)
└── infra
    └── ProductIconFactory.java  ← Flyweight Factory (풀 관리)""",
        "key_benefits": [
            "대량의 유사 객체 생성 시 메모리 사용량을 크게 줄입니다",
            "내부/외부 상태를 명확히 분리하여 객체 설계를 개선합니다",
            "Spring Bean 싱글턴과 유사한 원리로 익숙하게 적용할 수 있습니다",
        ],
    },

    "Proxy": {
        "pattern_name": "Proxy",
        "category": "structural",
        "overview": "다른 객체에 대한 접근을 제어하기 위해 대리자(Proxy) 객체를 제공하는 패턴입니다. 실제 객체에 대한 접근 전후로 추가 로직을 삽입할 수 있습니다.",
        "use_case": "지연 로딩, 캐싱, 접근 제어, 로깅을 위해 사용합니다. Spring AOP와 @Transactional, @Cacheable이 모두 프록시 패턴으로 구현됩니다. 직접 프록시 구현으로 원리를 이해할 수 있습니다.",
        "layers_used": ["contract", "application", "infra"],
        "flow_description": [
            "① UserService는 @Qualifier로 CachingUserRepositoryProxy를 주입받습니다.",
            "② findById() 호출 시 프록시가 먼저 캐시(Map)에서 id를 검색합니다.",
            "③ 캐시에 있으면 '캐시 히트' 로그를 남기고 DB 조회 없이 바로 반환합니다.",
            "④ 캐시에 없으면 실제 DatabaseUserRepository.findById()를 호출하여 DB를 조회합니다.",
            "⑤ DB 조회 결과를 캐시에 저장한 후 반환합니다.",
            "⑥ 다음 동일 id 요청부터는 캐시에서 즉시 반환됩니다 (Spring @Cacheable과 동일 원리)."
        ],
        "example_code": """\
// ===== [contract/UserRepository.java] =====
package com.example.proxy.contract;

import java.util.Optional;

// RealSubject와 Proxy가 모두 구현하는 인터페이스
public interface UserRepository {
    Optional<String> findById(Long id);
    void save(Long id, String username);
}

// ===== [infra/DatabaseUserRepository.java] =====
package com.example.proxy.infra;

import com.example.proxy.contract.UserRepository;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// RealSubject: 실제 DB 접근 구현체
@Repository
public class DatabaseUserRepository implements UserRepository {

    private final Map<Long, String> db = new HashMap<>(); // 실제: JPA 등

    @Override
    public Optional<String> findById(Long id) {
        System.out.println("[DB] 조회: id=" + id); // 실제 DB I/O 발생
        return Optional.ofNullable(db.get(id));
    }

    @Override
    public void save(Long id, String username) {
        System.out.println("[DB] 저장: id=" + id + ", name=" + username);
        db.put(id, username);
    }
}

// ===== [infra/CachingUserRepositoryProxy.java] =====
package com.example.proxy.infra;

import com.example.proxy.contract.UserRepository;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// Proxy: 캐싱 기능을 추가한 대리자 — 실제 구현체(RealSubject)를 감쌈
@Repository("cachingUserRepository") // Bean 이름으로 구분
public class CachingUserRepositoryProxy implements UserRepository {

    private final DatabaseUserRepository realRepository; // 실제 구현체 참조
    private final Map<Long, String> cache = new HashMap<>(); // 캐시 저장소

    public CachingUserRepositoryProxy(DatabaseUserRepository realRepository) {
        this.realRepository = realRepository;
    }

    @Override
    public Optional<String> findById(Long id) {
        if (cache.containsKey(id)) {
            System.out.println("[CACHE] 캐시 히트: id=" + id); // DB 호출 없이 반환
            return Optional.of(cache.get(id));
        }
        // 캐시 미스: 실제 DB 조회 후 캐시 저장
        Optional<String> result = realRepository.findById(id);
        result.ifPresent(name -> cache.put(id, name)); // 결과를 캐시에 저장
        return result;
    }

    @Override
    public void save(Long id, String username) {
        realRepository.save(id, username);
        cache.put(id, username); // DB 저장과 동시에 캐시도 갱신
    }
}

// ===== [application/UserService.java] =====
package com.example.proxy.application;

import com.example.proxy.contract.UserRepository;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;

    // @Qualifier로 프록시 구현체를 선택 주입
    public UserService(@Qualifier("cachingUserRepository") UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public String getUser(Long id) {
        return userRepository.findById(id).orElse("사용자 없음");
    }
}""",
        "package_structure": """\
com.example.proxy
├── contract
│   └── UserRepository.java
├── infra
│   ├── DatabaseUserRepository.java      ← RealSubject
│   └── CachingUserRepositoryProxy.java  ← Proxy (캐싱 추가)
└── application
    └── UserService.java""",
        "key_benefits": [
            "실제 객체 수정 없이 캐싱, 로깅, 접근 제어를 추가할 수 있습니다",
            "Spring @Cacheable, @Transactional의 동작 원리를 이해하는 데 도움이 됩니다",
            "@Qualifier로 프록시와 실제 구현체를 유연하게 교체할 수 있습니다",
        ],
    },

    # ══════════════════════════════════════════════════
    # BEHAVIORAL PATTERNS (행동 패턴)
    # ══════════════════════════════════════════════════

    "Chain of Responsibility": {
        "pattern_name": "Chain of Responsibility",
        "category": "behavioral",
        "overview": "요청을 처리할 수 있는 핸들러들을 체인으로 연결하고, 요청이 처리될 때까지 체인을 따라 전달하는 패턴입니다. 요청자와 처리자의 결합도를 낮춥니다.",
        "use_case": "주문 처리 시 인증 → 재고 확인 → 결제 검증처럼 순차적인 검증/처리 단계가 필요할 때 사용합니다. Spring Security의 Filter Chain이 이 패턴의 대표적인 구현입니다.",
        "layers_used": ["contract", "application"],
        "flow_description": [
            "① 핸들러들이 chain.setNext()로 연결됩니다: Auth → StockCheck → PaymentValidation.",
            "② AuthenticationHandler.handle()이 호출되며 process()로 인증을 확인합니다.",
            "③ 인증 실패 시 false를 반환하여 체인이 중단됩니다 — 다음 핸들러 미호출.",
            "④ 인증 성공(true 반환) 시 setNext로 연결된 StockCheckHandler에 자동으로 전달됩니다.",
            "⑤ 재고 확인, 결제 검증 핸들러도 동일하게 처리 → 전달 또는 중단.",
            "⑥ 모든 핸들러를 통과한 요청만 실제 주문 처리로 진행됩니다."
        ],
        "example_code": """\
// ===== [contract/OrderHandler.java] =====
package com.example.chainofresponsibility.contract;

// 추상 핸들러: 체인 연결 로직을 담당, 서브클래스는 process()만 구현
public abstract class OrderHandler {

    private OrderHandler next; // 다음 핸들러 참조

    // 체이닝 지원: handler1.setNext(handler2).setNext(handler3) 가능
    public OrderHandler setNext(OrderHandler next) {
        this.next = next;
        return next; // 다음 핸들러를 반환하여 연속 호출 지원
    }

    // 템플릿 메서드: 처리 → 전달 흐름을 강제
    public final void handle(OrderRequest request) {
        if (process(request) && next != null) { // 처리 성공 시에만 다음으로 전달
            next.handle(request);
        }
    }

    // 각 핸들러가 구현: true=다음 핸들러로 전달, false=체인 중단
    protected abstract boolean process(OrderRequest request);
}

// ===== [contract/OrderRequest.java] =====
package com.example.chainofresponsibility.contract;

import lombok.Data;

@Data
public class OrderRequest {
    private String  customerId;
    private String  productId;
    private int     quantity;
    private double  totalAmount;
    private boolean authenticated; // 인증 여부
}

// ===== [application/AuthenticationHandler.java] =====
package com.example.chainofresponsibility.application;

import com.example.chainofresponsibility.contract.OrderHandler;
import com.example.chainofresponsibility.contract.OrderRequest;
import org.springframework.stereotype.Component;

@Component
public class AuthenticationHandler extends OrderHandler {

    @Override
    protected boolean process(OrderRequest request) {
        if (!request.isAuthenticated()) {
            System.out.println("[인증 실패] 로그인이 필요합니다"); // 체인 중단
            return false;
        }
        System.out.println("[인증 통과] → 다음 핸들러로 전달");
        return true; // 다음 핸들러(StockCheckHandler)로 전달
    }
}

// ===== [application/StockCheckHandler.java] =====
package com.example.chainofresponsibility.application;

import com.example.chainofresponsibility.contract.OrderHandler;
import com.example.chainofresponsibility.contract.OrderRequest;
import org.springframework.stereotype.Component;

@Component
public class StockCheckHandler extends OrderHandler {

    @Override
    protected boolean process(OrderRequest request) {
        if (request.getQuantity() > 100) {
            System.out.println("[재고 부족] 최대 100개까지 주문 가능합니다"); // 체인 중단
            return false;
        }
        System.out.println("[재고 확인 완료] 수량: " + request.getQuantity() + " → 다음 핸들러로 전달");
        return true;
    }
}

// ===== [application/PaymentValidationHandler.java] =====
package com.example.chainofresponsibility.application;

import com.example.chainofresponsibility.contract.OrderHandler;
import com.example.chainofresponsibility.contract.OrderRequest;
import org.springframework.stereotype.Component;

@Component
public class PaymentValidationHandler extends OrderHandler {

    @Override
    protected boolean process(OrderRequest request) {
        if (request.getTotalAmount() <= 0) {
            System.out.println("[결제 검증 실패] 결제 금액이 올바르지 않습니다");
            return false;
        }
        System.out.println("[결제 검증 완료] 금액: " + request.getTotalAmount() + " → 주문 처리 진행");
        return true; // 모든 검증 통과 — 실제 주문 처리 가능
    }
}""",
        "package_structure": """\
com.example.chainofresponsibility
├── contract
│   ├── OrderHandler.java    ← 추상 핸들러 (체인 로직 포함)
│   └── OrderRequest.java
└── application
    ├── AuthenticationHandler.java       ← 1번째 핸들러
    ├── StockCheckHandler.java           ← 2번째 핸들러
    └── PaymentValidationHandler.java    ← 3번째 핸들러""",
        "key_benefits": [
            "처리 단계를 독립적인 핸들러로 분리하여 단일 책임 원칙을 지킵니다",
            "핸들러 추가/제거가 쉬워 처리 체인을 유연하게 구성할 수 있습니다",
            "Spring Security Filter Chain의 동작 원리와 동일하여 이해에 도움이 됩니다",
        ],
    },

    "Command": {
        "pattern_name": "Command",
        "category": "behavioral",
        "overview": "요청을 객체로 캡슐화하여 매개변수화, 큐에 저장, 로그, 실행 취소(Undo) 기능을 지원하는 패턴입니다. 요청 발신자와 수신자를 분리합니다.",
        "use_case": "주문 생성/취소처럼 실행 취소가 필요하거나, 작업을 큐에 저장하고 지연 실행해야 할 때 사용합니다. CQRS 패턴의 Command 부분과 직접 연결되어 Spring Boot 애플리케이션에 자주 활용됩니다.",
        "layers_used": ["contract", "domain", "application"],
        "flow_description": [
            "① 클라이언트가 Order 객체와 함께 CreateOrderCommand를 생성합니다.",
            "② OrderCommandInvoker.execute(command)를 호출하면 command.execute()가 실행됩니다.",
            "③ CreateOrderCommand.execute()가 Order의 상태를 CONFIRMED로 변경합니다.",
            "④ Invoker는 실행된 커맨드를 history 스택(Deque)에 push하여 저장합니다.",
            "⑤ undoLast() 호출 시 가장 최근 커맨드를 pop하고 undo()를 실행합니다.",
            "⑥ CreateOrderCommand.undo()가 Order 상태를 PENDING으로 되돌립니다."
        ],
        "example_code": """\
// ===== [contract/Command.java] =====
package com.example.command.contract;

// 모든 커맨드가 구현해야 하는 인터페이스
public interface Command {
    void execute(); // 명령 실행
    void undo();    // 실행 취소
}

// ===== [domain/Order.java] =====
package com.example.command.domain;

import lombok.Data;

@Data
public class Order {
    private String orderId;
    private String productId;
    private int    quantity;
    private String status; // PENDING → CONFIRMED → CANCELLED
}

// ===== [domain/CreateOrderCommand.java] =====
package com.example.command.domain;

import com.example.command.contract.Command;

// 주문 생성 커맨드: 실행/취소 로직을 객체로 캡슐화
public class CreateOrderCommand implements Command {

    private final Order order; // 수신자(Receiver): 실제 상태를 가진 객체

    public CreateOrderCommand(Order order) { this.order = order; }

    @Override
    public void execute() {
        order.setStatus("CONFIRMED"); // 주문 확정 처리
        System.out.println("[주문 생성] " + order.getOrderId() + " → CONFIRMED");
    }

    @Override
    public void undo() {
        order.setStatus("PENDING"); // 이전 상태로 되돌림
        System.out.println("[주문 생성 취소] " + order.getOrderId() + " → PENDING");
    }
}

// ===== [domain/CancelOrderCommand.java] =====
package com.example.command.domain;

import com.example.command.contract.Command;

// 주문 취소 커맨드: undo 시 이전 상태 복원을 위해 previousStatus 보관
public class CancelOrderCommand implements Command {

    private final Order  order;
    private       String previousStatus; // undo를 위해 이전 상태 저장

    public CancelOrderCommand(Order order) { this.order = order; }

    @Override
    public void execute() {
        previousStatus = order.getStatus(); // 현재 상태 백업
        order.setStatus("CANCELLED");
        System.out.println("[주문 취소] " + order.getOrderId() + " → CANCELLED");
    }

    @Override
    public void undo() {
        order.setStatus(previousStatus); // 백업해둔 이전 상태로 복원
        System.out.println("[주문 취소 복원] " + order.getOrderId() + " → " + previousStatus);
    }
}

// ===== [application/OrderCommandInvoker.java] =====
package com.example.command.application;

import com.example.command.contract.Command;
import org.springframework.stereotype.Service;

import java.util.ArrayDeque;
import java.util.Deque;

// Invoker: 커맨드 실행 및 이력 관리 담당
@Service
public class OrderCommandInvoker {

    private final Deque<Command> history = new ArrayDeque<>(); // 실행 이력 스택

    public void execute(Command command) {
        command.execute();      // 커맨드 실행
        history.push(command);  // 스택에 저장 (나중에 undo 가능하도록)
    }

    public void undoLast() {
        if (!history.isEmpty()) {
            history.pop().undo(); // 가장 최근 커맨드를 꺼내어 취소
        }
    }
}""",
        "package_structure": """\
com.example.command
├── contract
│   └── Command.java
├── domain
│   ├── Order.java
│   ├── CreateOrderCommand.java
│   └── CancelOrderCommand.java
└── application
    └── OrderCommandInvoker.java""",
        "key_benefits": [
            "요청을 객체로 캡슐화하여 실행 취소(Undo/Redo) 기능을 구현할 수 있습니다",
            "명령을 큐에 저장하고 지연 실행하거나 로깅하는 것이 가능합니다",
            "CQRS 패턴의 Command 부분과 자연스럽게 연결됩니다",
        ],
    },

    "Interpreter": {
        "pattern_name": "Interpreter",
        "category": "behavioral",
        "overview": "특정 언어나 표현식에 대한 문법을 정의하고 해석하는 패턴입니다. 각 규칙을 클래스로 표현하여 언어의 문장을 해석합니다.",
        "use_case": "할인 규칙 엔진('VIP이면서 구매금액이 10만원 이상이면 20% 할인')처럼 비즈니스 규칙을 표현식으로 정의하고 해석해야 할 때 사용합니다. Spring Expression Language(SpEL)가 이 패턴의 구현체입니다.",
        "layers_used": ["contract", "domain"],
        "flow_description": [
            "① DiscountRuleEngine에 VipDiscountExpression, MinAmountDiscountExpression이 규칙으로 등록됩니다.",
            "② calculateDiscount(context)가 호출되면 모든 규칙을 순회합니다.",
            "③ VipDiscountExpression.interpret(context)는 context.grade가 'VIP'인지 검사합니다.",
            "④ VIP인 경우 주문금액 × 20%를 할인금액으로 반환합니다.",
            "⑤ MinAmountDiscountExpression은 주문금액이 10만원 이상이면 5,000원을 반환합니다.",
            "⑥ 각 규칙의 반환값을 모두 합산하여 최종 할인금액을 계산합니다."
        ],
        "example_code": """\
// ===== [contract/DiscountExpression.java] =====
package com.example.interpreter.contract;

import com.example.interpreter.domain.CustomerContext;

// 인터프리터 패턴의 핵심: 모든 규칙(표현식)이 구현하는 인터페이스
public interface DiscountExpression {
    double interpret(CustomerContext context); // 컨텍스트를 해석하여 할인금액 반환
}

// ===== [domain/CustomerContext.java] =====
package com.example.interpreter.domain;

import lombok.Data;

// 문맥(Context): 규칙 해석에 필요한 데이터를 담은 객체
@Data
public class CustomerContext {
    private String  customerId;
    private String  grade;          // VIP, NORMAL
    private double  orderAmount;    // 주문 금액
    private boolean firstPurchase;  // 첫 구매 여부
}

// ===== [domain/VipDiscountExpression.java] =====
package com.example.interpreter.domain;

import com.example.interpreter.contract.DiscountExpression;

// 터미널 표현식: VIP 등급 할인 규칙
public class VipDiscountExpression implements DiscountExpression {

    private final double rate; // 할인율 (e.g., 0.20 = 20%)

    public VipDiscountExpression(double rate) { this.rate = rate; }

    @Override
    public double interpret(CustomerContext context) {
        if ("VIP".equals(context.getGrade())) {
            double discount = context.getOrderAmount() * rate;
            System.out.printf("[VIP 할인] %.0f원 × %.0f%% = -%.0f원%n",
                context.getOrderAmount(), rate * 100, discount);
            return discount; // VIP이면 할인금액 반환
        }
        return 0; // VIP 아니면 0
    }
}

// ===== [domain/MinAmountDiscountExpression.java] =====
package com.example.interpreter.domain;

import com.example.interpreter.contract.DiscountExpression;

// 터미널 표현식: 최소 구매금액 달성 시 정액 할인 규칙
public class MinAmountDiscountExpression implements DiscountExpression {

    private final double minAmount;      // 최소 구매금액 조건
    private final double discountAmount; // 할인 정액

    public MinAmountDiscountExpression(double minAmount, double discountAmount) {
        this.minAmount      = minAmount;
        this.discountAmount = discountAmount;
    }

    @Override
    public double interpret(CustomerContext context) {
        if (context.getOrderAmount() >= minAmount) {
            System.out.printf("[금액 할인] %.0f원 이상 → -%.0f원%n", minAmount, discountAmount);
            return discountAmount;
        }
        return 0;
    }
}

// ===== [domain/DiscountRuleEngine.java] =====
package com.example.interpreter.domain;

import com.example.interpreter.contract.DiscountExpression;
import org.springframework.stereotype.Component;

import java.util.List;

// 규칙 엔진: 등록된 모든 표현식(규칙)을 해석하여 총 할인금액 계산
@Component
public class DiscountRuleEngine {

    // 규칙 목록 — 새 규칙 추가 시 여기에만 추가
    private final List<DiscountExpression> rules;

    public DiscountRuleEngine() {
        this.rules = List.of(
            new VipDiscountExpression(0.20),                    // VIP: 20% 할인
            new MinAmountDiscountExpression(100_000, 5_000)     // 10만원 이상: 5천원 할인
        );
    }

    public double calculateDiscount(CustomerContext context) {
        // 모든 규칙을 순회하며 각 할인금액을 합산
        return rules.stream()
                    .mapToDouble(rule -> rule.interpret(context))
                    .sum();
    }
}""",
        "package_structure": """\
com.example.interpreter
├── contract
│   └── DiscountExpression.java
└── domain
    ├── CustomerContext.java
    ├── VipDiscountExpression.java
    ├── MinAmountDiscountExpression.java
    └── DiscountRuleEngine.java""",
        "key_benefits": [
            "비즈니스 규칙을 코드 변경 없이 조합하고 확장할 수 있습니다",
            "각 규칙이 독립적인 클래스로 분리되어 테스트가 용이합니다",
            "Spring SpEL의 동작 원리를 이해하는 데 도움이 됩니다",
        ],
    },

    "Iterator": {
        "pattern_name": "Iterator",
        "category": "behavioral",
        "overview": "컬렉션의 내부 구조를 노출하지 않고 요소들을 순차적으로 접근할 수 있는 방법을 제공하는 패턴입니다.",
        "use_case": "대용량 데이터를 페이지 단위로 순회하거나, 커스텀 컬렉션의 탐색 방법을 캡슐화할 때 사용합니다. Java의 Iterator 인터페이스와 Spring Data의 Page/Slice가 이 패턴을 구현합니다.",
        "layers_used": ["contract", "domain"],
        "flow_description": [
            "① ProductCollection에 상품 목록과 페이지 크기를 지정하여 생성합니다.",
            "② createIterator()를 호출하면 내부 PagedProductIterator가 생성됩니다.",
            "③ iterator.hasNext()로 다음 요소가 있는지 확인합니다.",
            "④ iterator.next()로 다음 상품을 가져오며, 내부 인덱스가 증가합니다.",
            "⑤ pageSize만큼 이동할 때마다 페이지 번호가 자동으로 증가합니다.",
            "⑥ 클라이언트는 내부가 List인지 배열인지 DB 커서인지 알 필요 없이 동일한 방법으로 순회합니다."
        ],
        "example_code": """\
// ===== [contract/ProductIterator.java] =====
package com.example.iterator.contract;

import com.example.iterator.domain.Product;

// 이터레이터 인터페이스: 컬렉션 순회 방법을 추상화
public interface ProductIterator {
    boolean hasNext();      // 다음 요소 존재 여부
    Product next();         // 다음 요소 반환 및 커서 이동
    int     currentPage();  // 현재 페이지 번호
}

// ===== [domain/Product.java] =====
package com.example.iterator.domain;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class Product {
    private Long   id;
    private String name;
    private double price;
}

// ===== [domain/ProductCollection.java] =====
package com.example.iterator.domain;

import com.example.iterator.contract.ProductIterator;

import java.util.List;

// 집합체(Aggregate): 이터레이터 생성 책임을 가짐
public class ProductCollection {

    private final List<Product> products;
    private final int           pageSize; // 페이지당 상품 수

    public ProductCollection(List<Product> products, int pageSize) {
        this.products = products;
        this.pageSize = pageSize;
    }

    // 이터레이터 생성 — 컬렉션 내부 구조는 외부에 노출되지 않음
    public ProductIterator createIterator() {
        return new PagedProductIterator(products, pageSize);
    }

    // 내부 이터레이터 구현 — 외부에서 직접 접근 불가
    private static class PagedProductIterator implements ProductIterator {

        private final List<Product> products;
        private final int           pageSize;
        private       int           currentIndex = 0; // 현재 커서 위치
        private       int           page         = 0; // 현재 페이지 번호

        PagedProductIterator(List<Product> products, int pageSize) {
            this.products = products;
            this.pageSize = pageSize;
        }

        @Override
        public boolean hasNext() {
            return currentIndex < products.size(); // 더 읽을 요소가 있는지 확인
        }

        @Override
        public Product next() {
            if (!hasNext()) throw new java.util.NoSuchElementException();
            Product product = products.get(currentIndex++); // 현재 요소 반환 후 커서 이동
            if (currentIndex % pageSize == 0) page++;        // 페이지 크기마다 페이지 번호 증가
            return product;
        }

        @Override
        public int currentPage() { return page; }
    }
}""",
        "package_structure": """\
com.example.iterator
├── contract
│   └── ProductIterator.java
└── domain
    ├── Product.java
    └── ProductCollection.java""",
        "key_benefits": [
            "컬렉션 내부 구조를 노출하지 않고 순회 방법을 캡슐화합니다",
            "페이지네이션 등 다양한 순회 전략을 독립적으로 구현할 수 있습니다",
            "Java Iterator 인터페이스, Spring Data Page와 동일한 원리입니다",
        ],
    },

    "Mediator": {
        "pattern_name": "Mediator",
        "category": "behavioral",
        "overview": "객체들이 서로 직접 참조하지 않고 중재자 객체를 통해서만 상호작용하게 하는 패턴입니다. 객체 간 결합도를 낮추고 상호작용을 중앙화합니다.",
        "use_case": "주문 완료 이벤트 발생 시 재고 차감, 이메일 발송, 포인트 적립 등 여러 서비스가 반응해야 할 때 사용합니다. Spring의 ApplicationEventPublisher/ApplicationEventListener가 이 패턴의 구현체입니다.",
        "layers_used": ["contract", "application", "domain"],
        "flow_description": [
            "① OrderService.completeOrder()가 주문 처리를 완료합니다.",
            "② 직접 InventoryService나 EmailService를 호출하지 않고, ApplicationEventPublisher(중재자)에 이벤트를 발행합니다.",
            "③ Spring의 이벤트 버스(중재자)가 OrderCompletedEvent를 받아 등록된 모든 리스너에 전달합니다.",
            "④ InventoryEventListener가 @EventListener로 이벤트를 받아 재고를 차감합니다.",
            "⑤ EmailEventListener도 동시에 이벤트를 받아 이메일을 발송합니다.",
            "⑥ 새 리스너(포인트 적립 등) 추가 시 OrderService 코드는 전혀 수정하지 않아도 됩니다."
        ],
        "example_code": """\
// ===== [domain/OrderCompletedEvent.java] =====
package com.example.mediator.domain;

import lombok.Getter;
import org.springframework.context.ApplicationEvent;

// 도메인 이벤트: 주문 완료 사실을 담은 불변 이벤트 객체
@Getter
public class OrderCompletedEvent extends ApplicationEvent {

    private final String orderId;
    private final String customerId;
    private final double amount;

    public OrderCompletedEvent(Object source, String orderId, String customerId, double amount) {
        super(source);
        this.orderId    = orderId;
        this.customerId = customerId;
        this.amount     = amount;
    }
}

// ===== [application/OrderService.java] =====
package com.example.mediator.application;

import com.example.mediator.domain.OrderCompletedEvent;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;

// 이벤트 발행자 (Publisher): 중재자에게 이벤트를 전달하는 역할
@Service
public class OrderService {

    // ApplicationEventPublisher = Spring의 중재자
    private final ApplicationEventPublisher eventPublisher;

    public OrderService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    public void completeOrder(String orderId, String customerId, double amount) {
        System.out.println("[주문 완료 처리] " + orderId);

        // 중재자를 통해 이벤트 발행 — 리스너들을 직접 호출하지 않음!
        eventPublisher.publishEvent(
            new OrderCompletedEvent(this, orderId, customerId, amount)
        );
        // 어떤 리스너가 있는지 OrderService는 알 필요 없음
    }
}

// ===== [application/InventoryEventListener.java] =====
package com.example.mediator.application;

import com.example.mediator.domain.OrderCompletedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

// 이벤트 수신자 1: 재고 차감 — OrderService와 직접 의존 없음
@Component
public class InventoryEventListener {

    @EventListener // Spring이 이 메서드를 자동으로 이벤트 리스너로 등록
    public void onOrderCompleted(OrderCompletedEvent event) {
        System.out.println("[재고 차감] 주문: " + event.getOrderId());
        // 실제: 재고 DB 업데이트
    }
}

// ===== [application/EmailEventListener.java] =====
package com.example.mediator.application;

import com.example.mediator.domain.OrderCompletedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

// 이벤트 수신자 2: 이메일 발송 — OrderService와 직접 의존 없음
@Component
public class EmailEventListener {

    @EventListener
    public void onOrderCompleted(OrderCompletedEvent event) {
        System.out.printf("[이메일 발송] 고객: %s, 주문: %s%n",
            event.getCustomerId(), event.getOrderId());
    }
}""",
        "package_structure": """\
com.example.mediator
├── domain
│   └── OrderCompletedEvent.java       ← 도메인 이벤트
└── application
    ├── OrderService.java              ← Publisher (이벤트 발행)
    ├── InventoryEventListener.java    ← Listener 1
    └── EmailEventListener.java        ← Listener 2""",
        "key_benefits": [
            "서비스 간 직접 의존성을 제거하여 결합도를 낮춥니다",
            "새로운 리스너 추가 시 기존 코드를 전혀 수정하지 않아도 됩니다",
            "Spring ApplicationEvent를 활용하면 추가 설정 없이 즉시 적용됩니다",
        ],
    },

    "Memento": {
        "pattern_name": "Memento",
        "category": "behavioral",
        "overview": "객체의 상태를 저장하고 이전 상태로 복원할 수 있게 하는 패턴입니다. 캡슐화를 유지하면서 객체의 스냅샷을 생성합니다.",
        "use_case": "주문 상태 변경 이력을 관리하거나, 문서 편집기의 Undo 기능처럼 이전 상태로 되돌려야 할 때 사용합니다. DB의 낙관적 락(Optimistic Lock)과 이벤트 소싱(Event Sourcing)의 기반 개념입니다.",
        "layers_used": ["domain"],
        "flow_description": [
            "① Order 생성 후 첫 상태를 history.save()로 저장합니다 (PENDING 스냅샷 생성).",
            "② order.confirm()으로 상태를 변경하고 다시 history.save()로 저장합니다 (CONFIRMED 스냅샷).",
            "③ history.undo() 호출 시 현재 스냅샷을 제거하고 이전 스냅샷을 꺼냅니다.",
            "④ Order.restoreFromMemento()가 꺼낸 스냅샷의 상태값으로 Order를 복원합니다.",
            "⑤ OrderMemento는 불변 객체로 외부에서 수정할 수 없어 안전하게 상태를 보관합니다.",
            "⑥ Order 내부 구조(필드)가 변해도 Memento/Caretaker 코드는 변경이 최소화됩니다."
        ],
        "example_code": """\
// ===== [domain/OrderMemento.java] =====
package com.example.memento.domain;

// Memento: 상태 스냅샷 — 불변 객체, 외부에서 수정 불가
public class OrderMemento {

    // 저장된 상태 — 모두 private final (불변)
    private final String status;
    private final double amount;
    private final String savedAt;

    public OrderMemento(String status, double amount, String savedAt) {
        this.status  = status;
        this.amount  = amount;
        this.savedAt = savedAt;
    }

    // Getter만 제공 — Setter 없음 (불변성 보장)
    public String getStatus()  { return status; }
    public double getAmount()  { return amount; }
    public String getSavedAt() { return savedAt; }
}

// ===== [domain/Order.java] =====
package com.example.memento.domain;

import java.time.LocalDateTime;

// Originator: 자신의 상태를 Memento로 저장하고 복원하는 객체
public class Order {

    private String orderId;
    private String status; // 현재 상태
    private double amount;

    public Order(String orderId, double amount) {
        this.orderId = orderId;
        this.status  = "PENDING";
        this.amount  = amount;
    }

    public void confirm() {
        this.status = "CONFIRMED";
        System.out.println("[주문 확인] " + orderId + " → CONFIRMED");
    }

    public void ship() {
        this.status = "SHIPPED";
        System.out.println("[배송 시작] " + orderId + " → SHIPPED");
    }

    // 현재 상태를 Memento(스냅샷)로 저장
    public OrderMemento saveToMemento() {
        return new OrderMemento(status, amount, LocalDateTime.now().toString());
    }

    // Memento(스냅샷)에서 상태 복원
    public void restoreFromMemento(OrderMemento memento) {
        this.status = memento.getStatus();
        this.amount = memento.getAmount();
        System.out.println("[상태 복원] " + orderId + " → " + status);
    }

    public String getStatus()  { return status; }
    public String getOrderId() { return orderId; }
}

// ===== [domain/OrderHistory.java] =====
package com.example.memento.domain;

import org.springframework.stereotype.Component;

import java.util.ArrayDeque;
import java.util.Deque;

// Caretaker: Memento 목록을 관리, Order 내부 구조는 모름
@Component
public class OrderHistory {

    // 이력 스택 — 가장 최근 상태가 맨 위에 위치
    private final Deque<OrderMemento> history = new ArrayDeque<>();

    public void save(Order order) {
        history.push(order.saveToMemento()); // 현재 상태 스냅샷 저장
        System.out.println("[이력 저장] 상태: " + order.getStatus());
    }

    public void undo(Order order) {
        if (history.size() > 1) {
            history.pop();                              // 현재 상태 제거
            order.restoreFromMemento(history.peek());   // 바로 이전 상태로 복원 (제거 안함)
        } else {
            System.out.println("[복원 불가] 더 이전 상태가 없습니다");
        }
    }
}""",
        "package_structure": """\
com.example.memento
└── domain
    ├── OrderMemento.java   ← Memento (불변 스냅샷)
    ├── Order.java          ← Originator (상태 보유 및 저장/복원)
    └── OrderHistory.java   ← Caretaker (이력 스택 관리)""",
        "key_benefits": [
            "캡슐화를 깨지 않고 객체 상태를 저장하고 복원할 수 있습니다",
            "Undo/Redo 기능 구현이 간단해집니다",
            "이벤트 소싱(Event Sourcing) 패턴의 기반 개념으로 활용됩니다",
        ],
    },

    "Observer": {
        "pattern_name": "Observer",
        "category": "behavioral",
        "overview": "객체의 상태 변화를 다수의 관찰자(Observer)에게 자동으로 통지하는 패턴입니다. 1:N 의존 관계를 정의하며 느슨한 결합을 유지합니다.",
        "use_case": "주문 상태 변경 시 이메일, SMS, 푸시 알림을 동시에 발송해야 할 때 사용합니다. Spring의 @EventListener와 ApplicationEventPublisher가 옵저버 패턴의 구현이며, DomainEvent와 함께 DDD에서 자주 활용됩니다.",
        "layers_used": ["contract", "domain", "application"],
        "flow_description": [
            "① Order에 addObserver()로 이메일/SMS 옵저버를 등록합니다.",
            "② order.changeStatus(\"CONFIRMED\")가 호출되면 Order 내부 상태가 변경됩니다.",
            "③ 상태 변경 후 notifyObservers()가 모든 등록된 옵저버에 이벤트를 전달합니다.",
            "④ EmailNotificationObserver.onStatusChanged()가 호출되어 이메일을 발송합니다.",
            "⑤ SmsNotificationObserver도 동일한 이벤트를 받아 독립적으로 SMS를 발송합니다.",
            "⑥ 새 옵저버 추가 시 Order 코드는 변경하지 않고 addObserver()만 호출합니다."
        ],
        "example_code": """\
// ===== [contract/OrderStatusObserver.java] =====
package com.example.observer.contract;

import com.example.observer.domain.OrderStatusChangedEvent;

// 옵저버 인터페이스: 모든 구독자가 구현해야 하는 계약
public interface OrderStatusObserver {
    void onStatusChanged(OrderStatusChangedEvent event);
}

// ===== [domain/OrderStatusChangedEvent.java] =====
package com.example.observer.domain;

import lombok.Getter;

// 이벤트 객체: 상태 변경에 대한 정보를 담은 불변 VO
@Getter
public class OrderStatusChangedEvent {
    private final String orderId;
    private final String previousStatus; // 변경 전 상태
    private final String newStatus;      // 변경 후 상태
    private final String customerId;

    public OrderStatusChangedEvent(String orderId, String previousStatus,
                                   String newStatus, String customerId) {
        this.orderId        = orderId;
        this.previousStatus = previousStatus;
        this.newStatus      = newStatus;
        this.customerId     = customerId;
    }
}

// ===== [domain/Order.java] =====
package com.example.observer.domain;

import com.example.observer.contract.OrderStatusObserver;

import java.util.ArrayList;
import java.util.List;

// Subject(발행자): 옵저버 목록을 관리하고 상태 변경 시 통보
public class Order {

    private String orderId;
    private String status;
    private String customerId;
    private final List<OrderStatusObserver> observers = new ArrayList<>(); // 옵저버 목록

    public Order(String orderId, String customerId) {
        this.orderId    = orderId;
        this.status     = "PENDING";
        this.customerId = customerId;
    }

    public void addObserver(OrderStatusObserver observer)    { observers.add(observer); }    // 구독 등록
    public void removeObserver(OrderStatusObserver observer) { observers.remove(observer); } // 구독 해제

    public void changeStatus(String newStatus) {
        String previous = this.status;
        this.status = newStatus; // 상태 변경

        // 상태 변경 후 모든 옵저버에 통보
        notifyObservers(new OrderStatusChangedEvent(orderId, previous, newStatus, customerId));
    }

    private void notifyObservers(OrderStatusChangedEvent event) {
        observers.forEach(obs -> obs.onStatusChanged(event)); // 1:N 통보
    }
}

// ===== [application/EmailNotificationObserver.java] =====
package com.example.observer.application;

import com.example.observer.contract.OrderStatusObserver;
import com.example.observer.domain.OrderStatusChangedEvent;
import org.springframework.stereotype.Component;

// 구체 옵저버 1: 이메일 발송 — Order와 직접 의존 없음
@Component
public class EmailNotificationObserver implements OrderStatusObserver {

    @Override
    public void onStatusChanged(OrderStatusChangedEvent event) {
        System.out.printf("[이메일] 고객 %s 주문 %s: %s → %s%n",
            event.getCustomerId(), event.getOrderId(),
            event.getPreviousStatus(), event.getNewStatus());
    }
}""",
        "package_structure": """\
com.example.observer
├── contract
│   └── OrderStatusObserver.java
├── domain
│   ├── OrderStatusChangedEvent.java
│   └── Order.java                      ← Subject (발행자)
└── application
    ├── EmailNotificationObserver.java   ← Observer 1
    └── SmsNotificationObserver.java     ← Observer 2""",
        "key_benefits": [
            "상태 변경 주체와 반응 객체 간의 결합도를 최소화합니다",
            "새로운 옵저버 추가 시 Subject 코드를 전혀 수정하지 않아도 됩니다",
            "Spring @EventListener와 결합하면 더욱 강력한 이벤트 기반 아키텍처를 구성할 수 있습니다",
        ],
    },

    "State": {
        "pattern_name": "State",
        "category": "behavioral",
        "overview": "객체의 내부 상태가 변경될 때 행동도 함께 변경되는 패턴입니다. 상태를 클래스로 캡슐화하여 if/switch 분기를 제거합니다.",
        "use_case": "주문의 상태(PENDING → CONFIRMED → SHIPPED → DELIVERED)에 따라 허용되는 행동이 달라지는 상태 머신을 구현할 때 사용합니다. Spring StateMachine 라이브러리도 이 패턴을 기반으로 합니다.",
        "layers_used": ["contract", "domain"],
        "flow_description": [
            "① Order 생성 시 초기 상태로 PendingState가 설정됩니다.",
            "② order.confirm() 호출 → 현재 상태(PendingState).confirm(this)가 실행됩니다.",
            "③ PendingState는 유효한 전환이므로 ctx.setState(new ConfirmedState())를 호출합니다.",
            "④ 이후 order.ship() → ConfirmedState.ship()이 실행되어 ShippedState로 전환됩니다.",
            "⑤ 잘못된 전환 시도(예: ShippedState에서 cancel()) 시 오류 메시지만 출력하고 상태는 유지됩니다.",
            "⑥ if/switch 없이 각 상태 클래스가 자신의 허용 행동을 스스로 관리합니다."
        ],
        "example_code": """\
// ===== [contract/OrderState.java] =====
package com.example.state.contract;

// 모든 상태 클래스가 구현해야 하는 인터페이스
public interface OrderState {
    void confirm(OrderContext context);  // 주문 확인
    void ship(OrderContext context);     // 배송 시작
    void deliver(OrderContext context);  // 배달 완료
    void cancel(OrderContext context);   // 취소
    String getStateName();               // 상태명 반환
}

// ===== [contract/OrderContext.java] =====
package com.example.state.contract;

// Context 인터페이스: 상태 전환 메서드 정의
public interface OrderContext {
    void       setState(OrderState state); // 상태 교체
    OrderState getState();
}

// ===== [domain/Order.java] =====
package com.example.state.domain;

import com.example.state.contract.OrderContext;
import com.example.state.contract.OrderState;

// Context: 현재 상태를 보유하고 상태 객체에 행동을 위임
public class Order implements OrderContext {

    private OrderState currentState; // 현재 상태 (런타임에 교체됨)
    private final String orderId;

    public Order(String orderId) {
        this.orderId      = orderId;
        this.currentState = new PendingState(); // 초기 상태: PENDING
    }

    @Override public void       setState(OrderState state) { this.currentState = state; }
    @Override public OrderState getState()                 { return currentState; }

    // 모든 행동을 현재 상태 객체에 위임 — if/switch 없음
    public void confirm()  { currentState.confirm(this); }
    public void ship()     { currentState.ship(this); }
    public void deliver()  { currentState.deliver(this); }
    public void cancel()   { currentState.cancel(this); }

    public String getStatus()  { return currentState.getStateName(); }
    public String getOrderId() { return orderId; }
}

// ===== [domain/PendingState.java] =====
package com.example.state.domain;

import com.example.state.contract.OrderContext;
import com.example.state.contract.OrderState;

// PENDING 상태: confirm(확인)과 cancel(취소)만 가능
public class PendingState implements OrderState {

    @Override
    public void confirm(OrderContext ctx) {
        System.out.println("[전환] PENDING → CONFIRMED");
        ctx.setState(new ConfirmedState()); // 다음 상태로 전환
    }

    @Override public void ship(OrderContext ctx)    { System.out.println("[오류] 확인 전 배송 불가"); }
    @Override public void deliver(OrderContext ctx) { System.out.println("[오류] 확인 전 배달 불가"); }

    @Override
    public void cancel(OrderContext ctx) {
        System.out.println("[전환] PENDING → CANCELLED");
        ctx.setState(new CancelledState());
    }

    @Override public String getStateName() { return "PENDING"; }
}

// ===== [domain/ConfirmedState.java] =====
package com.example.state.domain;

import com.example.state.contract.OrderContext;
import com.example.state.contract.OrderState;

// CONFIRMED 상태: ship(배송)과 cancel(취소)만 가능
public class ConfirmedState implements OrderState {

    @Override public void confirm(OrderContext ctx) { System.out.println("[오류] 이미 확인된 주문"); }

    @Override
    public void ship(OrderContext ctx) {
        System.out.println("[전환] CONFIRMED → SHIPPED");
        ctx.setState(new ShippedState());
    }

    @Override public void deliver(OrderContext ctx) { System.out.println("[오류] 배송 전 배달 불가"); }

    @Override
    public void cancel(OrderContext ctx) {
        System.out.println("[전환] CONFIRMED → CANCELLED");
        ctx.setState(new CancelledState());
    }

    @Override public String getStateName() { return "CONFIRMED"; }
}

// ===== [domain/ShippedState.java / DeliveredState.java / CancelledState.java] =====
package com.example.state.domain;

import com.example.state.contract.OrderContext;
import com.example.state.contract.OrderState;

// SHIPPED 상태: deliver만 가능 (배송 중 취소 불가)
public class ShippedState implements OrderState {

    @Override public void confirm(OrderContext ctx) { System.out.println("[오류] 이미 배송 중"); }
    @Override public void ship(OrderContext ctx)    { System.out.println("[오류] 이미 배송 중"); }

    @Override
    public void deliver(OrderContext ctx) {
        System.out.println("[전환] SHIPPED → DELIVERED");
        ctx.setState(new DeliveredState());
    }

    @Override public void cancel(OrderContext ctx) { System.out.println("[오류] 배송 중 취소 불가"); }
    @Override public String getStateName()         { return "SHIPPED"; }
}""",
        "package_structure": """\
com.example.state
├── contract
│   ├── OrderState.java    ← 상태 인터페이스
│   └── OrderContext.java
└── domain
    ├── Order.java          ← Context (상태 위임)
    ├── PendingState.java
    ├── ConfirmedState.java
    ├── ShippedState.java
    ├── DeliveredState.java
    └── CancelledState.java""",
        "key_benefits": [
            "복잡한 if/switch 분기를 제거하여 상태별 행동을 명확하게 분리합니다",
            "새로운 상태 추가 시 기존 상태 클래스를 수정하지 않아도 됩니다",
            "Spring StateMachine 라이브러리의 동작 원리와 동일합니다",
        ],
    },

    "Strategy": {
        "pattern_name": "Strategy",
        "category": "behavioral",
        "overview": "알고리즘 군을 정의하고 캡슐화하여 상호 교환 가능하게 만드는 패턴입니다. 클라이언트와 독립적으로 알고리즘을 변경할 수 있습니다.",
        "use_case": "할인 전략(정률/정액/회원등급)처럼 동일한 목적의 알고리즘이 여러 개 있고, 런타임에 전략을 교체해야 할 때 사용합니다. Spring의 @Qualifier나 Map 주입과 결합하면 강력한 전략 선택 메커니즘을 구현할 수 있습니다.",
        "layers_used": ["contract", "domain", "application"],
        "flow_description": [
            "① OrderDiscountService 생성 시 Spring이 DiscountStrategy 구현체들을 Map으로 자동 주입합니다.",
            "② Map의 키는 Bean 이름(@Component의 value), 값은 전략 구현체입니다.",
            "③ applyDiscount(\"percentageDiscount\", price) 호출 시 Map에서 해당 전략을 찾습니다.",
            "④ PercentageDiscountStrategy.calculateDiscount()가 가격 × 10%를 계산하여 반환합니다.",
            "⑤ 서비스는 최종 가격(원가 - 할인금액)을 계산하여 반환합니다.",
            "⑥ 새 전략 추가 시 DiscountStrategy 구현체 클래스 하나만 추가하면 됩니다 — 서비스 코드 무변경."
        ],
        "example_code": """\
// ===== [contract/DiscountStrategy.java] =====
package com.example.strategy.contract;

// 전략 인터페이스: 모든 할인 알고리즘이 구현해야 하는 계약
public interface DiscountStrategy {
    double calculateDiscount(double originalPrice); // 할인금액 반환
    String getStrategyName();                       // 전략 식별자
}

// ===== [domain/PercentageDiscountStrategy.java] =====
package com.example.strategy.domain;

import com.example.strategy.contract.DiscountStrategy;
import org.springframework.stereotype.Component;

// 전략 1: 정률 할인 (10%)
@Component("percentageDiscount") // Bean 이름 = Map의 키
public class PercentageDiscountStrategy implements DiscountStrategy {

    private final double rate;

    public PercentageDiscountStrategy() { this.rate = 0.10; } // 10% 할인

    @Override
    public double calculateDiscount(double originalPrice) {
        double discount = originalPrice * rate; // 원가 × 할인율
        System.out.printf("[정률 할인] %.0f원 × %.0f%% = -%.0f원%n",
            originalPrice, rate * 100, discount);
        return discount;
    }

    @Override public String getStrategyName() { return "percentageDiscount"; }
}

// ===== [domain/FixedAmountDiscountStrategy.java] =====
package com.example.strategy.domain;

import com.example.strategy.contract.DiscountStrategy;
import org.springframework.stereotype.Component;

// 전략 2: 정액 할인 (3,000원)
@Component("fixedAmountDiscount")
public class FixedAmountDiscountStrategy implements DiscountStrategy {

    private final double discountAmount;

    public FixedAmountDiscountStrategy() { this.discountAmount = 3_000; }

    @Override
    public double calculateDiscount(double originalPrice) {
        double discount = Math.min(discountAmount, originalPrice); // 원가보다 큰 할인 방지
        System.out.printf("[정액 할인] -%.0f원%n", discount);
        return discount;
    }

    @Override public String getStrategyName() { return "fixedAmountDiscount"; }
}

// ===== [domain/VipMemberDiscountStrategy.java] =====
package com.example.strategy.domain;

import com.example.strategy.contract.DiscountStrategy;
import org.springframework.stereotype.Component;

// 전략 3: VIP 회원 할인 (20%)
@Component("vipMemberDiscount")
public class VipMemberDiscountStrategy implements DiscountStrategy {

    @Override
    public double calculateDiscount(double originalPrice) {
        double discount = originalPrice * 0.20;
        System.out.printf("[VIP 할인] %.0f원 × 20%% = -%.0f원%n", originalPrice, discount);
        return discount;
    }

    @Override public String getStrategyName() { return "vipMemberDiscount"; }
}

// ===== [application/OrderDiscountService.java] =====
package com.example.strategy.application;

import com.example.strategy.contract.DiscountStrategy;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class OrderDiscountService {

    // Spring이 DiscountStrategy 구현체들을 {빈이름: 구현체} Map으로 자동 주입
    private final Map<String, DiscountStrategy> strategies;

    public OrderDiscountService(Map<String, DiscountStrategy> strategies) {
        this.strategies = strategies;
        // strategies = {
        //   "percentageDiscount": PercentageDiscountStrategy,
        //   "fixedAmountDiscount": FixedAmountDiscountStrategy,
        //   "vipMemberDiscount": VipMemberDiscountStrategy
        // }
    }

    public double applyDiscount(String strategyName, double price) {
        DiscountStrategy strategy = strategies.get(strategyName); // 전략 선택
        if (strategy == null) throw new IllegalArgumentException("전략 없음: " + strategyName);

        double discount   = strategy.calculateDiscount(price);
        double finalPrice = price - discount;
        System.out.printf("[최종 가격] %.0f원%n", finalPrice);
        return finalPrice;
    }
}""",
        "package_structure": """\
com.example.strategy
├── contract
│   └── DiscountStrategy.java
├── domain
│   ├── PercentageDiscountStrategy.java   ← 전략 1
│   ├── FixedAmountDiscountStrategy.java  ← 전략 2
│   └── VipMemberDiscountStrategy.java    ← 전략 3
└── application
    └── OrderDiscountService.java""",
        "key_benefits": [
            "알고리즘을 캡슐화하여 런타임에 전략을 자유롭게 교체할 수 있습니다",
            "새로운 할인 전략 추가 시 기존 코드를 전혀 수정하지 않아도 됩니다",
            "Spring의 Map 자동 주입으로 별도 팩토리 없이 전략 선택이 가능합니다",
        ],
    },

    "Template Method": {
        "pattern_name": "Template Method",
        "category": "behavioral",
        "overview": "알고리즘의 뼈대(골격)를 상위 클래스에서 정의하고, 일부 단계를 서브클래스에서 구현하도록 하는 패턴입니다. 공통 흐름은 유지하면서 세부 구현을 변경할 수 있습니다.",
        "use_case": "Excel, PDF, CSV처럼 형식은 다르지만 데이터 추출 → 변환 → 출력의 공통 흐름이 있는 리포트 생성에 사용합니다. Spring의 JdbcTemplate, RestTemplate도 이 패턴으로 구현되어 있습니다.",
        "layers_used": ["contract", "application", "domain"],
        "flow_description": [
            "① ExcelReportGenerator.generate(data)를 호출합니다.",
            "② 부모 클래스(ReportGenerator)의 generate() — 템플릿 메서드 — 가 실행됩니다.",
            "③ 템플릿 메서드 내부에서 extractData() → formatData() → createHeader() → createFooter() 순으로 호출합니다.",
            "④ extractData()와 formatData()는 abstract이므로 ExcelReportGenerator의 구현이 실행됩니다.",
            "⑤ createHeader()는 서브클래스가 오버라이드했으므로 Excel 전용 헤더가 적용됩니다.",
            "⑥ 모든 단계의 결과를 조합하여 최종 보고서 문자열을 반환합니다."
        ],
        "example_code": """\
// ===== [contract/ReportGenerator.java] =====
package com.example.templatemethod.contract;

import com.example.templatemethod.domain.ReportData;

// 템플릿 메서드 패턴의 핵심: 알고리즘 골격을 final로 정의
public abstract class ReportGenerator {

    // 템플릿 메서드: 전체 흐름을 정의, final로 서브클래스 변경 방지
    public final String generate(ReportData data) {
        String extracted = extractData(data);       // 1단계: 데이터 추출 (서브클래스 구현)
        String formatted = formatData(extracted);   // 2단계: 형식 변환 (서브클래스 구현)
        String header    = createHeader(data.getTitle()); // 3단계: 헤더 생성
        String footer    = createFooter();          // 4단계: 푸터 생성
        return header + "\\n" + formatted + "\\n" + footer; // 조합하여 반환
    }

    // 추상 메서드: 서브클래스에서 반드시 구현해야 함 (형식별 핵심 로직)
    protected abstract String extractData(ReportData data);
    protected abstract String formatData(String rawData);

    // Hook 메서드: 기본 구현 제공, 서브클래스가 선택적으로 오버라이드 가능
    protected String createHeader(String title) {
        return "=== " + title + " ==="; // 기본 헤더
    }

    protected String createFooter() {
        return "=== 보고서 끝 ==="; // 기본 푸터
    }
}

// ===== [domain/ReportData.java] =====
package com.example.templatemethod.domain;

import lombok.Data;
import java.util.List;

@Data
public class ReportData {
    private String       title;
    private List<String> rows;        // 데이터 행 목록
    private String       generatedAt; // 생성 일시
}

// ===== [application/ExcelReportGenerator.java] =====
package com.example.templatemethod.application;

import com.example.templatemethod.contract.ReportGenerator;
import com.example.templatemethod.domain.ReportData;
import org.springframework.stereotype.Component;

// Excel 전용 보고서 생성기: 추상 메서드만 구현
@Component("excelReport")
public class ExcelReportGenerator extends ReportGenerator {

    @Override
    protected String extractData(ReportData data) {
        return String.join(",", data.getRows()); // CSV 형식으로 데이터 추출
    }

    @Override
    protected String formatData(String rawData) {
        return "[Excel 데이터]\\n" + rawData.replace(",", "\\t"); // 탭 구분으로 Excel 형식 변환
    }

    @Override // 선택적 오버라이드: Excel 전용 헤더로 변경
    protected String createHeader(String title) {
        return "Excel 보고서: " + title + " (Sheet1)";
    }
    // createFooter()는 오버라이드 안 함 — 기본 구현 사용
}

// ===== [application/CsvReportGenerator.java] =====
package com.example.templatemethod.application;

import com.example.templatemethod.contract.ReportGenerator;
import com.example.templatemethod.domain.ReportData;
import org.springframework.stereotype.Component;

// CSV 전용 보고서 생성기
@Component("csvReport")
public class CsvReportGenerator extends ReportGenerator {

    @Override
    protected String extractData(ReportData data) {
        return String.join("\\n", data.getRows()); // 줄바꿈 구분
    }

    @Override
    protected String formatData(String rawData) {
        return "[CSV 데이터]\\n" + rawData; // CSV 형식 그대로 사용
    }
    // createHeader(), createFooter() 오버라이드 안 함 — 기본 구현 사용
}""",
        "package_structure": """\
com.example.templatemethod
├── contract
│   └── ReportGenerator.java   ← 템플릿 메서드 (abstract)
├── domain
│   └── ReportData.java
└── application
    ├── ExcelReportGenerator.java   ← 구체 구현
    ├── CsvReportGenerator.java     ← 구체 구현
    └── PdfReportGenerator.java     ← 구체 구현""",
        "key_benefits": [
            "공통 알고리즘 흐름을 상위 클래스에서 한 번만 정의하여 코드 중복을 제거합니다",
            "전체 흐름을 변경하지 않고 세부 단계만 서브클래스에서 커스터마이징할 수 있습니다",
            "Spring JdbcTemplate, RestTemplate의 동작 원리와 동일합니다",
        ],
    },

    "Visitor": {
        "pattern_name": "Visitor",
        "category": "behavioral",
        "overview": "객체의 구조는 변경하지 않으면서 새로운 연산(기능)을 추가할 수 있는 패턴입니다. 연산을 별도의 Visitor 객체로 분리합니다.",
        "use_case": "장바구니 항목(일반 상품, 배송비, 할인 쿠폰)에 금액 계산, 세금 계산, 리포트 생성 등 다양한 연산을 추가해야 할 때 사용합니다. 기존 클래스를 수정하지 않고 새 기능을 추가하는 OCP를 강하게 지원합니다.",
        "layers_used": ["contract", "domain"],
        "flow_description": [
            "① TotalPriceCalculator(방문자)가 장바구니 항목 목록을 순회합니다.",
            "② 각 항목(ProductItem, ShippingItem 등)의 accept(visitor)가 호출됩니다.",
            "③ accept() 내부에서 visitor.visit(this)를 호출하여 자신의 타입을 명시적으로 전달합니다.",
            "④ TotalPriceCalculator가 오버로딩된 visit() 중 해당 타입의 메서드를 실행합니다.",
            "⑤ ProductItem은 가격×수량, ShippingItem은 배송비, DiscountItem은 -할인금액을 반환합니다.",
            "⑥ 모든 항목의 반환값을 합산하여 최종 금액을 계산합니다. 새 계산 방식 추가 시 새 Visitor 클래스만 추가합니다."
        ],
        "example_code": """\
// ===== [contract/CartItemVisitor.java] =====
package com.example.visitor.contract;

import com.example.visitor.domain.ProductItem;
import com.example.visitor.domain.ShippingItem;
import com.example.visitor.domain.DiscountItem;

// 방문자 인터페이스: 각 항목 타입에 대한 visit() 메서드 정의
// 새 연산 추가 시 이 인터페이스를 구현한 새 Visitor 클래스를 만들면 됨
public interface CartItemVisitor {
    double visit(ProductItem  item);  // 상품 항목 방문
    double visit(ShippingItem item);  // 배송비 항목 방문
    double visit(DiscountItem item);  // 할인 항목 방문
}

// ===== [contract/CartItem.java] =====
package com.example.visitor.contract;

// 모든 장바구니 항목의 인터페이스: accept()로 방문자를 받아들임
public interface CartItem {
    double accept(CartItemVisitor visitor); // 방문자에게 자신을 전달
    String getDescription();
}

// ===== [domain/ProductItem.java] =====
package com.example.visitor.domain;

import com.example.visitor.contract.CartItem;
import com.example.visitor.contract.CartItemVisitor;

public class ProductItem implements CartItem {

    private final String name;
    private final double price;
    private final int    quantity;

    public ProductItem(String name, double price, int quantity) {
        this.name     = name;
        this.price    = price;
        this.quantity = quantity;
    }

    @Override
    public double accept(CartItemVisitor visitor) {
        return visitor.visit(this); // Double Dispatch: 자신의 타입으로 올바른 visit() 호출 유도
    }

    @Override public String getDescription() { return name + " × " + quantity; }
    public double getPrice()    { return price; }
    public int    getQuantity() { return quantity; }
}

// ===== [domain/ShippingItem.java] =====
package com.example.visitor.domain;

import com.example.visitor.contract.CartItem;
import com.example.visitor.contract.CartItemVisitor;

public class ShippingItem implements CartItem {

    private final double shippingFee;

    public ShippingItem(double shippingFee) { this.shippingFee = shippingFee; }

    @Override
    public double accept(CartItemVisitor visitor) { return visitor.visit(this); }

    @Override public String getDescription()  { return "배송비"; }
    public double getShippingFee()            { return shippingFee; }
}

// ===== [domain/DiscountItem.java] =====
package com.example.visitor.domain;

import com.example.visitor.contract.CartItem;
import com.example.visitor.contract.CartItemVisitor;

public class DiscountItem implements CartItem {

    private final double discountAmount;

    public DiscountItem(double discountAmount) { this.discountAmount = discountAmount; }

    @Override
    public double accept(CartItemVisitor visitor) { return visitor.visit(this); }

    @Override public String getDescription()  { return "할인 쿠폰"; }
    public double getDiscountAmount()         { return discountAmount; }
}

// ===== [domain/TotalPriceCalculator.java] =====
package com.example.visitor.domain;

import com.example.visitor.contract.CartItem;
import com.example.visitor.contract.CartItemVisitor;
import org.springframework.stereotype.Component;

import java.util.List;

// 구체 방문자: 총 금액 계산 — 각 항목을 방문하여 금액 합산
@Component
public class TotalPriceCalculator implements CartItemVisitor {

    @Override
    public double visit(ProductItem item) {
        return item.getPrice() * item.getQuantity(); // 상품: 단가 × 수량
    }

    @Override
    public double visit(ShippingItem item) {
        return item.getShippingFee(); // 배송비: 그대로 합산
    }

    @Override
    public double visit(DiscountItem item) {
        return -item.getDiscountAmount(); // 할인: 음수로 처리 (차감)
    }

    // 전체 장바구니 합계 계산
    public double calculate(List<CartItem> items) {
        return items.stream()
                    .mapToDouble(item -> item.accept(this)) // 각 항목에 방문자 전달
                    .sum();
    }
}""",
        "package_structure": """\
com.example.visitor
├── contract
│   ├── CartItemVisitor.java   ← Visitor 인터페이스
│   └── CartItem.java          ← Element 인터페이스 (accept 보유)
└── domain
    ├── ProductItem.java
    ├── ShippingItem.java
    ├── DiscountItem.java
    └── TotalPriceCalculator.java  ← Concrete Visitor""",
        "key_benefits": [
            "기존 클래스를 수정하지 않고 새로운 연산(세금 계산, 리포트 등)을 추가할 수 있습니다",
            "관련 연산을 하나의 Visitor 클래스에 집중시켜 응집도를 높입니다",
            "OCP(개방-폐쇄 원칙)를 강하게 지원합니다",
        ],
    },

    # ══════════════════════════════════════════════════
    # DDD PATTERNS (도메인 주도 설계 패턴)
    # ══════════════════════════════════════════════════

    "Aggregate Root": {
        "pattern_name": "Aggregate Root",
        "category": "ddd",
        "overview": "연관된 도메인 객체들을 하나의 일관성 경계로 묶고, 외부에서 내부 객체에 직접 접근하지 못하도록 루트 엔티티가 모든 접근을 통제하는 DDD 패턴입니다. 불변식(Invariant)은 항상 Aggregate 경계 안에서 유지됩니다.",
        "use_case": "Order(주문)와 OrderItem(주문 항목)처럼 생명주기를 공유하는 객체 그룹에서 사용합니다. '최소 1개 상품', '최대 주문금액 100만원' 같은 비즈니스 규칙을 Aggregate Root가 책임집니다. Spring Data JPA에서는 Aggregate Root만 Repository를 가집니다.",
        "layers_used": ["domain", "application"],
        "flow_description": [
            "① 클라이언트가 Order.create(customerId, items)를 호출합니다 (정적 팩토리 메서드).",
            "② Order.create() 내부에서 items가 비어 있으면 즉시 예외를 발생시킵니다 (불변식 보호).",
            "③ Order 생성 후 총금액이 100만 원을 초과하면 예외를 발생시킵니다 (금액 불변식).",
            "④ 주문 항목 추가는 반드시 order.addItem()을 통해서만 가능합니다 — items 컬렉션 직접 접근 불가.",
            "⑤ OrderApplicationService가 Order를 생성하고 OrderRepository.save()로 저장합니다.",
            "⑥ Repository는 Order(Aggregate Root)만 저장하며, OrderItem은 Order와 함께 영속화됩니다.",
            "⑦ 조회 시에도 OrderRepository를 통해서만 접근 — OrderItem만 별도 조회하는 경우는 없습니다."
        ],
        "example_code": """\
// ===== [domain/OrderItem.java] =====
package com.example.aggregateroot.domain;

import jakarta.persistence.*;
import lombok.Getter;

// 내부 엔티티: Aggregate Root(Order)를 통해서만 접근 가능
@Entity
@Getter
public class OrderItem {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String productId;
    private int    quantity;
    private long   unitPrice;

    protected OrderItem() {} // JPA 전용 기본 생성자

    // 패키지 접근자: Order만 생성 가능 (외부 직접 생성 차단)
    OrderItem(String productId, int quantity, long unitPrice) {
        if (quantity <= 0) throw new IllegalArgumentException("수량은 1 이상이어야 합니다");
        this.productId = productId;
        this.quantity  = quantity;
        this.unitPrice = unitPrice;
    }

    public long subtotal() { return unitPrice * quantity; } // 항목 소계
}

// ===== [domain/Order.java] =====
package com.example.aggregateroot.domain;

import jakarta.persistence.*;
import lombok.Getter;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

// Aggregate Root: 모든 불변식 보호 및 내부 객체 접근 통제
@Entity
@Table(name = "orders")
@Getter
public class Order {

    private static final long MAX_ORDER_AMOUNT = 1_000_000L; // 최대 주문금액 100만원

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String        customerId;
    private String        status;
    private LocalDateTime orderedAt;

    // CascadeType.ALL: Order 저장 시 OrderItem도 함께 영속화
    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "order_id")
    private List<OrderItem> items = new ArrayList<>();

    protected Order() {} // JPA 전용 기본 생성자

    // 정적 팩토리 메서드: 불변식 검증 후 Order 생성
    public static Order create(String customerId, List<OrderItem> items) {
        if (items == null || items.isEmpty())
            throw new IllegalArgumentException("주문 항목은 최소 1개 이상이어야 합니다"); // 불변식 1

        Order order = new Order();
        order.customerId = customerId;
        order.status     = "PENDING";
        order.orderedAt  = LocalDateTime.now();
        order.items.addAll(items);

        long totalAmount = order.calculateTotal();
        if (totalAmount > MAX_ORDER_AMOUNT)
            throw new IllegalArgumentException("주문 금액이 최대 한도를 초과합니다: " + totalAmount); // 불변식 2

        return order;
    }

    // 항목 추가는 반드시 이 메서드를 통해서만 — 직접 items.add() 불가
    public void addItem(String productId, int quantity, long unitPrice) {
        OrderItem item = new OrderItem(productId, quantity, unitPrice);
        long newTotal = calculateTotal() + item.subtotal();
        if (newTotal > MAX_ORDER_AMOUNT)
            throw new IllegalArgumentException("항목 추가 시 최대 주문금액 초과");
        items.add(item);
    }

    public void confirm() {
        if (!"PENDING".equals(status)) throw new IllegalStateException("대기 중인 주문만 확인 가능합니다");
        this.status = "CONFIRMED"; // 상태 전환 — 불변식 내에서만 허용
    }

    public long calculateTotal() {
        return items.stream().mapToLong(OrderItem::subtotal).sum();
    }

    // 외부에는 불변 뷰만 제공 — 내부 컬렉션 직접 수정 차단
    public List<OrderItem> getItems() { return Collections.unmodifiableList(items); }
}

// ===== [application/OrderApplicationService.java] =====
package com.example.aggregateroot.application;

import com.example.aggregateroot.domain.Order;
import com.example.aggregateroot.domain.OrderItem;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class OrderApplicationService {

    private final OrderRepository orderRepository;

    public OrderApplicationService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @Transactional
    public Long placeOrder(String customerId, List<OrderItemRequest> requests) {
        // Aggregate Root 생성 (불변식 검증 포함)
        List<OrderItem> items = requests.stream()
            .map(r -> new OrderItem(r.productId(), r.quantity(), r.unitPrice()))
            .toList();
        Order order = Order.create(customerId, items); // 불변식 위반 시 예외
        orderRepository.save(order); // Aggregate Root만 저장 — OrderItem은 cascade로 처리
        return order.getId();
    }
}""",
        "package_structure": """\
com.example.aggregateroot
├── domain
│   ├── Order.java          ← Aggregate Root (불변식 보호)
│   └── OrderItem.java      ← 내부 엔티티 (직접 접근 불가)
└── application
    ├── OrderApplicationService.java
    └── OrderRepository.java""",
        "key_benefits": [
            "불변식(Invariant)을 Aggregate Root 한 곳에서 보호하여 데이터 일관성을 보장합니다",
            "내부 엔티티 직접 접근을 차단하여 도메인 규칙을 우회하는 코드를 방지합니다",
            "Spring Data JPA의 Cascade 전략과 자연스럽게 연계됩니다",
        ],
    },

    "Value Object": {
        "pattern_name": "Value Object",
        "category": "ddd",
        "overview": "식별자 없이 속성 값으로만 동등성을 판단하는 불변 객체입니다. Setter가 없으며 상태 변경 시 새 객체를 반환합니다. JPA의 @Embeddable로 엔티티에 포함할 수 있습니다.",
        "use_case": "금액(Money), 주소(Address), 이메일(Email)처럼 원시 타입만으로 표현하면 의미가 불분명한 값에 사용합니다. 'Long price'보다 'Money price'가 통화 정보와 유효성 검사를 함께 표현합니다.",
        "layers_used": ["domain"],
        "flow_description": [
            "① Money.of(10000, \"KRW\")로 값 객체를 생성합니다 (정적 팩토리, 유효성 검사 포함).",
            "② Money는 불변이므로 add() 호출 시 새 Money 객체를 반환합니다 (기존 객체 불변).",
            "③ 두 Money의 equals()는 참조가 아닌 amount와 currency 값으로 비교합니다.",
            "④ @Embeddable 덕분에 Order 엔티티에 Money가 컬럼으로 직접 매핑됩니다.",
            "⑤ Address도 마찬가지로 @Embeddable로 여러 컬럼으로 펼쳐집니다.",
            "⑥ 값 객체 내부에 비즈니스 규칙(음수 금지, 다른 통화 덧셈 불가)이 캡슐화됩니다."
        ],
        "example_code": """\
// ===== [domain/Money.java] =====
package com.example.valueobject.domain;

import jakarta.persistence.Embeddable;
import java.math.BigDecimal;
import java.util.Objects;

// Value Object: 금액과 통화를 하나의 의미 단위로 표현
@Embeddable // JPA: Order 테이블에 amount, currency 컬럼으로 매핑
public class Money {

    private final BigDecimal amount;   // 금액
    private final String     currency; // 통화 코드 (KRW, USD 등)

    protected Money() { this.amount = BigDecimal.ZERO; this.currency = "KRW"; } // JPA 전용

    private Money(BigDecimal amount, String currency) {
        if (amount.compareTo(BigDecimal.ZERO) < 0)
            throw new IllegalArgumentException("금액은 0 이상이어야 합니다"); // 도메인 규칙
        this.amount   = amount;
        this.currency = currency;
    }

    // 정적 팩토리: 의미 있는 생성 방법 제공
    public static Money of(long amount, String currency) {
        return new Money(BigDecimal.valueOf(amount), currency);
    }

    // 불변: 덧셈 시 새 객체 반환 (this는 변하지 않음)
    public Money add(Money other) {
        if (!this.currency.equals(other.currency))
            throw new IllegalArgumentException("다른 통화끼리 덧셈 불가: " + currency + " vs " + other.currency);
        return new Money(this.amount.add(other.amount), this.currency);
    }

    public Money multiply(int multiplier) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(multiplier)), this.currency);
    }

    public boolean isGreaterThan(Money other) {
        return this.amount.compareTo(other.amount) > 0;
    }

    // 값으로 동등성 비교 — 참조(identity)가 아님
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money)) return false;
        Money money = (Money) o;
        return Objects.equals(amount, money.amount) &&
               Objects.equals(currency, money.currency);
    }

    @Override public int hashCode() { return Objects.hash(amount, currency); }
    @Override public String toString() { return amount.toPlainString() + " " + currency; }

    public BigDecimal getAmount()   { return amount; }
    public String     getCurrency() { return currency; }
}

// ===== [domain/Address.java] =====
package com.example.valueobject.domain;

import jakarta.persistence.Embeddable;
import java.util.Objects;

// Value Object: 배송 주소 — 변경 시 새 Address 객체를 생성
@Embeddable
public class Address {

    private final String city;       // 시/도
    private final String street;     // 도로명 주소
    private final String zipCode;    // 우편번호

    protected Address() { this.city = ""; this.street = ""; this.zipCode = ""; } // JPA 전용

    public Address(String city, String street, String zipCode) {
        if (city == null || street == null || zipCode == null)
            throw new IllegalArgumentException("주소 구성요소는 null일 수 없습니다");
        this.city    = city;
        this.street  = street;
        this.zipCode = zipCode;
    }

    // 일부만 변경할 때: 새 객체 반환 (불변성 유지)
    public Address withCity(String newCity) {
        return new Address(newCity, this.street, this.zipCode);
    }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof Address)) return false;
        Address a = (Address) o;
        return Objects.equals(city, a.city) &&
               Objects.equals(street, a.street) &&
               Objects.equals(zipCode, a.zipCode);
    }

    @Override public int    hashCode()  { return Objects.hash(city, street, zipCode); }
    @Override public String toString()  { return zipCode + " " + city + " " + street; }

    public String getCity()    { return city; }
    public String getStreet()  { return street; }
    public String getZipCode() { return zipCode; }
}

// ===== [domain/Order.java] =====
package com.example.valueobject.domain;

import jakarta.persistence.*;
import lombok.Getter;

// 엔티티: Value Object를 @Embedded로 포함
@Entity
@Table(name = "orders")
@Getter
public class Order {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String customerId;

    @Embedded // Money → (amount, currency) 컬럼으로 매핑
    private Money totalAmount;

    @Embedded // Address → (city, street, zip_code) 컬럼으로 매핑
    private Address shippingAddress;

    protected Order() {}

    public Order(String customerId, Money totalAmount, Address shippingAddress) {
        this.customerId      = customerId;
        this.totalAmount     = totalAmount;
        this.shippingAddress = shippingAddress;
    }

    // 배송 주소 변경: Value Object 교체 (내부 수정이 아닌 새 객체 할당)
    public void changeShippingAddress(Address newAddress) {
        this.shippingAddress = newAddress;
    }
}""",
        "package_structure": """\
com.example.valueobject
└── domain
    ├── Money.java    ← Value Object (금액 + 통화)
    ├── Address.java  ← Value Object (배송 주소)
    └── Order.java    ← Entity (@Embedded로 VO 포함)""",
        "key_benefits": [
            "원시 타입 집착(Primitive Obsession)을 제거하고 도메인 개념을 명확히 표현합니다",
            "불변성 덕분에 스레드 안전하며 공유해도 안전합니다",
            "@Embeddable로 JPA 매핑이 간결해지고 도메인 로직이 VO 안에 캡슐화됩니다",
        ],
    },

    "Domain Event": {
        "pattern_name": "Domain Event",
        "category": "ddd",
        "overview": "도메인에서 발생한 중요한 사실(과거형)을 이벤트 객체로 표현하여 다른 컴포넌트에 비동기적으로 전파하는 패턴입니다. 도메인 로직과 부수 효과(이메일, 알림 등)를 분리합니다.",
        "use_case": "주문 완료 시 재고 차감, 이메일 발송, 포인트 적립을 Order 도메인이 직접 처리하지 않고 OrderPlacedEvent를 발행합니다. Spring ApplicationEventPublisher와 @EventListener로 구현합니다.",
        "layers_used": ["domain", "application", "infra"],
        "flow_description": [
            "① OrderApplicationService가 Order.place()를 호출하여 주문을 생성합니다.",
            "② Order.place() 내부에서 OrderPlacedEvent를 생성하고 내부 이벤트 목록에 등록합니다.",
            "③ OrderApplicationService가 orderRepository.save(order) 후 등록된 이벤트를 꺼내 발행합니다.",
            "④ Spring ApplicationEventPublisher가 OrderPlacedEvent를 모든 리스너에 전달합니다.",
            "⑤ NotificationEventHandler가 @EventListener로 이벤트를 받아 이메일을 발송합니다.",
            "⑥ InventoryEventHandler도 동일 이벤트를 받아 재고를 예약합니다.",
            "⑦ Order 도메인은 알림/재고 서비스에 의존하지 않으므로 도메인 순수성이 유지됩니다."
        ],
        "example_code": """\
// ===== [domain/OrderPlacedEvent.java] =====
package com.example.domainevent.domain;

import lombok.Getter;
import org.springframework.context.ApplicationEvent;

import java.time.LocalDateTime;

// 도메인 이벤트: "주문이 접수되었다"는 과거 사실을 담은 불변 객체
@Getter
public class OrderPlacedEvent extends ApplicationEvent {

    private final String        orderId;
    private final String        customerId;
    private final long          totalAmount;
    private final LocalDateTime occurredAt; // 이벤트 발생 시각

    public OrderPlacedEvent(Object source, String orderId, String customerId, long totalAmount) {
        super(source);
        this.orderId      = orderId;
        this.customerId   = customerId;
        this.totalAmount  = totalAmount;
        this.occurredAt   = LocalDateTime.now();
    }
}

// ===== [domain/Order.java] =====
package com.example.domainevent.domain;

import jakarta.persistence.*;
import lombok.Getter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "orders")
@Getter
public class Order {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String orderId;
    private String customerId;
    private long   totalAmount;
    private String status;

    // 미발행 도메인 이벤트 목록 — DB에 저장되지 않음
    @Transient
    private final List<Object> domainEvents = new ArrayList<>();

    protected Order() {}

    // 주문 접수: 비즈니스 로직 수행 후 도메인 이벤트 등록
    public static Order place(String orderId, String customerId, long totalAmount) {
        Order order       = new Order();
        order.orderId     = orderId;
        order.customerId  = customerId;
        order.totalAmount = totalAmount;
        order.status      = "PLACED";

        // 이벤트를 직접 발행하지 않고 목록에 등록 (저장 후 발행하기 위해)
        order.domainEvents.add(new OrderPlacedEvent(order, orderId, customerId, totalAmount));
        return order;
    }

    // 등록된 이벤트를 꺼내고 목록을 비움 (한 번만 발행)
    public List<Object> pullDomainEvents() {
        List<Object> events = new ArrayList<>(domainEvents);
        domainEvents.clear();
        return events;
    }
}

// ===== [application/OrderApplicationService.java] =====
package com.example.domainevent.application;

import com.example.domainevent.domain.Order;
import com.example.domainevent.domain.OrderRepository;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderApplicationService {

    private final OrderRepository       orderRepository;
    private final ApplicationEventPublisher eventPublisher; // Spring 이벤트 버스

    public OrderApplicationService(OrderRepository orderRepository,
                                   ApplicationEventPublisher eventPublisher) {
        this.orderRepository = orderRepository;
        this.eventPublisher  = eventPublisher;
    }

    @Transactional
    public String placeOrder(String customerId, long totalAmount) {
        String orderId = "ORD-" + System.currentTimeMillis();
        Order order = Order.place(orderId, customerId, totalAmount); // 이벤트 등록
        orderRepository.save(order);                                 // DB 저장

        // 트랜잭션 커밋 전 이벤트 발행 (동기) — 비동기는 @TransactionalEventListener 사용
        order.pullDomainEvents().forEach(eventPublisher::publishEvent);
        return orderId;
    }
}

// ===== [infra/NotificationEventHandler.java] =====
package com.example.domainevent.infra;

import com.example.domainevent.domain.OrderPlacedEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

// 이벤트 핸들러: Order 도메인과 무관하게 독립 존재
@Component
public class NotificationEventHandler {

    // OrderPlacedEvent 발행 시 자동 호출 — Order와 직접 의존 없음
    @EventListener
    public void handle(OrderPlacedEvent event) {
        System.out.printf("[이메일 발송] 고객 %s님, 주문 %s 접수 완료 (금액: %d원)%n",
            event.getCustomerId(), event.getOrderId(), event.getTotalAmount());
        // 실제: EmailService.send(event.getCustomerId(), ...)
    }
}""",
        "package_structure": """\
com.example.domainevent
├── domain
│   ├── Order.java              ← Aggregate Root (이벤트 등록)
│   ├── OrderPlacedEvent.java   ← 도메인 이벤트 (불변)
│   └── OrderRepository.java
├── application
│   └── OrderApplicationService.java  ← 이벤트 발행
└── infra
    └── NotificationEventHandler.java ← 이벤트 처리""",
        "key_benefits": [
            "도메인 로직과 부수 효과(알림, 재고 등)를 완전히 분리하여 응집도를 높입니다",
            "새로운 리액션 추가 시 도메인 코드 변경 없이 리스너만 추가합니다",
            "이벤트 저장(Event Sourcing)으로 확장하면 감사 로그와 재처리가 자연스럽게 지원됩니다",
        ],
    },

    "Repository": {
        "pattern_name": "Repository",
        "category": "ddd",
        "overview": "도메인 객체 컬렉션에 대한 인터페이스를 제공하여 영속성 기술(JPA, MyBatis 등)을 도메인으로부터 격리하는 DDD 패턴입니다. 단순 CRUD가 아닌 도메인 언어로 메서드를 정의합니다.",
        "use_case": "주문 도메인에서 findByCustomerId, findPendingOrders처럼 비즈니스 의도가 명확한 메서드를 정의합니다. contract 레이어에 인터페이스를 두고 infra 레이어에서 JPA로 구현하면 도메인이 JPA에 의존하지 않습니다.",
        "layers_used": ["contract", "domain", "infra"],
        "flow_description": [
            "① contract 레이어에 OrderRepository 인터페이스를 도메인 언어로 정의합니다.",
            "② domain 레이어의 Order Aggregate Root만 Repository를 가집니다 (OrderItem은 없음).",
            "③ infra 레이어의 JpaOrderRepository가 Spring Data JPA로 인터페이스를 구현합니다.",
            "④ application 레이어는 OrderRepository 인터페이스에만 의존 — JPA 직접 의존 없음.",
            "⑤ findByCustomerIdAndStatus()처럼 도메인 의도가 드러나는 메서드를 사용합니다.",
            "⑥ JPA 구현을 MyBatis나 다른 기술로 교체해도 domain/application 코드는 그대로입니다."
        ],
        "example_code": """\
// ===== [contract/OrderRepository.java] =====
package com.example.repository.contract;

import com.example.repository.domain.Order;

import java.util.List;
import java.util.Optional;

// DDD Repository 인터페이스: 도메인 언어로 메서드 정의 (JPA 용어 없음)
public interface OrderRepository {

    void             save(Order order);              // 저장 (신규 + 수정)
    Optional<Order>  findById(Long id);              // ID로 단건 조회
    List<Order>      findByCustomerId(String customerId); // 고객별 주문 목록
    List<Order>      findPendingOrders();            // 미처리 주문 조회 (비즈니스 메서드)
    List<Order>      findByCustomerIdAndStatus(String customerId, String status); // 복합 조건
    void             delete(Order order);            // 삭제
    boolean          existsById(Long id);            // 존재 여부 확인
}

// ===== [domain/Order.java] =====
package com.example.repository.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

// Aggregate Root: Repository의 저장/조회 대상
@Entity
@Table(name = "orders")
@Getter @Setter
public class Order {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String        customerId;
    private String        status;      // PENDING, CONFIRMED, SHIPPED, DELIVERED
    private long          totalAmount;
    private LocalDateTime orderedAt;

    protected Order() {}

    public Order(String customerId, long totalAmount) {
        this.customerId  = customerId;
        this.totalAmount = totalAmount;
        this.status      = "PENDING";
        this.orderedAt   = LocalDateTime.now();
    }

    public void confirm() {
        if (!"PENDING".equals(status)) throw new IllegalStateException("대기 주문만 확인 가능");
        this.status = "CONFIRMED";
    }
}

// ===== [infra/JpaOrderRepository.java] =====
package com.example.repository.infra;

import com.example.repository.contract.OrderRepository;
import com.example.repository.domain.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

// JPA 구현체: contract 인터페이스 구현 + Spring Data JPA 확장
@Repository
public interface JpaOrderRepository extends OrderRepository, JpaRepository<Order, Long> {

    // Spring Data JPA 메서드 네이밍으로 자동 구현
    List<Order> findByCustomerId(String customerId);

    List<Order> findByCustomerIdAndStatus(String customerId, String status);

    // JPQL: 비즈니스 의도가 명확한 "미처리 주문" 조회
    @Query("SELECT o FROM Order o WHERE o.status = 'PENDING' ORDER BY o.orderedAt ASC")
    List<Order> findPendingOrders();

    // JpaRepository가 이미 제공: save(), findById(), delete(), existsById()
    // → OrderRepository의 나머지 메서드는 JpaRepository가 자동 구현
}

// ===== [application/OrderQueryService.java] =====
package com.example.repository.application;

import com.example.repository.contract.OrderRepository; // JPA가 아닌 인터페이스에 의존
import com.example.repository.domain.Order;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional(readOnly = true)
public class OrderQueryService {

    private final OrderRepository orderRepository; // 구현체(JPA)에 직접 의존하지 않음

    public OrderQueryService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public List<Order> getCustomerOrders(String customerId) {
        return orderRepository.findByCustomerId(customerId); // 도메인 언어 메서드 사용
    }

    public List<Order> getPendingOrders() {
        return orderRepository.findPendingOrders(); // 비즈니스 의도가 명확한 메서드
    }
}""",
        "package_structure": """\
com.example.repository
├── contract
│   └── OrderRepository.java      ← 도메인 언어 인터페이스
├── domain
│   └── Order.java                ← Aggregate Root
├── infra
│   └── JpaOrderRepository.java   ← JPA 구현체
└── application
    └── OrderQueryService.java""",
        "key_benefits": [
            "도메인이 JPA, MyBatis 등 영속성 기술에 직접 의존하지 않아 테스트가 쉬워집니다",
            "도메인 언어로 Repository 메서드를 정의하여 의도가 명확해집니다",
            "영속성 기술 교체 시 infra 레이어만 수정하면 됩니다",
        ],
    },

    "Domain Service": {
        "pattern_name": "Domain Service",
        "category": "ddd",
        "overview": "단일 엔티티나 값 객체에 속하지 않는 도메인 로직을 캡슐화하는 서비스입니다. 도메인 전문가의 언어로 표현되며 인프라에 의존하지 않습니다. Application Service와 달리 순수 도메인 로직만 담습니다.",
        "use_case": "배송비 계산처럼 Order의 무게와 배송지 Address를 동시에 참조해야 하는 로직은 어느 한 엔티티에 속하지 않습니다. ShippingFeePolicy 도메인 서비스가 여러 도메인 객체를 조합하여 계산합니다.",
        "layers_used": ["domain", "application"],
        "flow_description": [
            "① OrderApplicationService가 주문 생성 요청을 받습니다.",
            "② shippingFeePolicy.calculate(order, destination)를 호출합니다.",
            "③ ShippingFeePolicy는 order.getTotalWeight()와 destination.getRegion()을 조합하여 배송비를 계산합니다.",
            "④ 계산 결과(Money)를 Order에 설정합니다.",
            "⑤ Domain Service는 인프라(DB, HTTP)에 의존하지 않아 단위 테스트가 쉽습니다.",
            "⑥ 배송비 정책이 바뀌면 ShippingFeePolicy 구현만 교체하면 됩니다."
        ],
        "example_code": """\
// ===== [domain/Money.java] =====
package com.example.domainservice.domain;

// 금액 값 객체 (간략 버전)
public record Money(long amount, String currency) {
    public static Money of(long amount) { return new Money(amount, "KRW"); }
    public Money add(Money other)       { return new Money(this.amount + other.amount, currency); }
    @Override public String toString()  { return amount + " " + currency; }
}

// ===== [domain/Address.java] =====
package com.example.domainservice.domain;

// 주소 값 객체
public record Address(String city, String region, String zipCode) {
    // 도서 지역 여부: 배송비 추가 적용
    public boolean isRemoteArea() {
        return "제주".equals(region) || "울릉".equals(region);
    }
}

// ===== [domain/Order.java] =====
package com.example.domainservice.domain;

import java.util.List;

// 주문 Aggregate Root — 배송비 계산 로직을 직접 보유하지 않음
public class Order {

    private final String     orderId;
    private final String     customerId;
    private final List<Item> items;      // 주문 항목 목록
    private       Money      shippingFee; // 배송비 (Domain Service가 설정)

    public Order(String orderId, String customerId, List<Item> items) {
        this.orderId    = orderId;
        this.customerId = customerId;
        this.items      = items;
    }

    // 총 무게 계산: Order 자체 책임
    public int getTotalWeightGrams() {
        return items.stream().mapToInt(Item::weightGrams).sum();
    }

    // 배송비는 Domain Service가 계산 후 주입
    public void applyShippingFee(Money fee) { this.shippingFee = fee; }

    public Money      getShippingFee() { return shippingFee; }
    public String     getOrderId()     { return orderId; }
    public String     getCustomerId()  { return customerId; }

    public record Item(String productId, int quantity, int weightGrams) {}
}

// ===== [domain/ShippingFeePolicy.java] =====
package com.example.domainservice.domain;

import org.springframework.stereotype.Component;

// Domain Service: 여러 도메인 객체를 조합한 비즈니스 로직 — 인프라 의존 없음
@Component
public class ShippingFeePolicy {

    private static final int    FREE_SHIPPING_THRESHOLD  = 50_000; // 5만원 이상 무료
    private static final long   BASE_FEE                 = 3_000;  // 기본 배송비
    private static final long   HEAVY_SURCHARGE          = 2_000;  // 무거운 상품 추가요금
    private static final long   REMOTE_AREA_SURCHARGE    = 5_000;  // 도서 지역 추가요금
    private static final int    HEAVY_WEIGHT_THRESHOLD   = 5_000;  // 5kg 이상 = 중량 상품

    // Order와 Address 두 도메인 객체를 조합 — 어느 한 객체에 속하지 않음
    public Money calculate(Order order, Address destination, long orderTotalAmount) {
        if (orderTotalAmount >= FREE_SHIPPING_THRESHOLD) {
            return Money.of(0); // 일정 금액 이상 무료 배송
        }

        long fee = BASE_FEE;

        // 무게 기반 추가요금
        if (order.getTotalWeightGrams() > HEAVY_WEIGHT_THRESHOLD) {
            fee += HEAVY_SURCHARGE;
            System.out.println("[배송비] 중량 추가요금 적용: +" + HEAVY_SURCHARGE);
        }

        // 도서 지역 추가요금 — Address 도메인 로직 활용
        if (destination.isRemoteArea()) {
            fee += REMOTE_AREA_SURCHARGE;
            System.out.println("[배송비] 도서 지역 추가요금 적용: +" + REMOTE_AREA_SURCHARGE);
        }

        System.out.println("[배송비 계산] 최종: " + fee + "원");
        return Money.of(fee);
    }
}

// ===== [application/OrderApplicationService.java] =====
package com.example.domainservice.application;

import com.example.domainservice.domain.*;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class OrderApplicationService {

    private final ShippingFeePolicy shippingFeePolicy; // Domain Service 주입

    public OrderApplicationService(ShippingFeePolicy shippingFeePolicy) {
        this.shippingFeePolicy = shippingFeePolicy;
    }

    public Order createOrder(String customerId, List<Order.Item> items,
                             Address destination, long orderTotalAmount) {
        Order order = new Order("ORD-001", customerId, items);

        // Domain Service로 배송비 계산 (Application Service는 조율만 담당)
        Money shippingFee = shippingFeePolicy.calculate(order, destination, orderTotalAmount);
        order.applyShippingFee(shippingFee);

        System.out.println("[주문 생성] " + order.getOrderId() + " 배송비: " + shippingFee);
        return order;
    }
}""",
        "package_structure": """\
com.example.domainservice
├── domain
│   ├── Order.java              ← Aggregate Root
│   ├── Money.java              ← Value Object
│   ├── Address.java            ← Value Object
│   └── ShippingFeePolicy.java  ← Domain Service (핵심)
└── application
    └── OrderApplicationService.java""",
        "key_benefits": [
            "어느 엔티티에도 자연스럽지 않은 도메인 로직을 명시적인 서비스로 표현합니다",
            "인프라에 의존하지 않아 순수 단위 테스트가 가능합니다",
            "정책 변경 시 Domain Service 구현만 교체하면 도메인 모델은 그대로 유지됩니다",
        ],
    },

    "Application Service": {
        "pattern_name": "Application Service",
        "category": "ddd",
        "overview": "도메인 레이어와 외부(presentation, infra)를 연결하는 얇은 조율 레이어입니다. 트랜잭션 경계, 권한 확인, 도메인 객체 로드/저장, 이벤트 발행을 담당하며 비즈니스 로직 자체는 도메인에 위임합니다.",
        "use_case": "주문 처리 흐름(Repository에서 Order 로드 → 도메인 메서드 호출 → 저장 → 이벤트 발행)을 OrderApplicationService가 조율합니다. 두꺼운 서비스(Fat Service)를 방지하고 도메인 로직은 Order에 집중시킵니다.",
        "layers_used": ["application", "presentation"],
        "flow_description": [
            "① OrderController가 PlaceOrderCommand DTO를 받아 OrderApplicationService.placeOrder()를 호출합니다.",
            "② Application Service가 @Transactional 범위 안에서 도메인 객체를 생성합니다.",
            "③ 비즈니스 로직은 Order.place()에 위임 — Application Service는 직접 구현하지 않습니다.",
            "④ orderRepository.save(order)로 저장합니다.",
            "⑤ 도메인 이벤트를 꺼내 ApplicationEventPublisher로 발행합니다.",
            "⑥ OrderSummaryDto를 조립하여 Presentation 레이어로 반환합니다.",
            "⑦ 예외 발생 시 @Transactional이 롤백을 처리합니다."
        ],
        "example_code": """\
// ===== [application/PlaceOrderCommand.java] =====
package com.example.applicationservice.application;

import java.util.List;

// Command DTO: Presentation → Application 데이터 전달 (도메인 객체 노출 없음)
public record PlaceOrderCommand(
    String        customerId,
    List<ItemDto> items
) {
    public record ItemDto(String productId, int quantity, long unitPrice) {}
}

// ===== [application/OrderSummaryDto.java] =====
package com.example.applicationservice.application;

import java.time.LocalDateTime;

// Response DTO: Application → Presentation 반환 (도메인 객체 노출 없음)
public record OrderSummaryDto(
    Long          orderId,
    String        status,
    long          totalAmount,
    LocalDateTime orderedAt
) {}

// ===== [application/OrderApplicationService.java] =====
package com.example.applicationservice.application;

import com.example.applicationservice.domain.Order;
import com.example.applicationservice.domain.OrderItem;
import com.example.applicationservice.domain.OrderRepository;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

// Application Service: 얇은 조율 레이어 (비즈니스 로직은 도메인에 위임)
@Service
public class OrderApplicationService {

    private final OrderRepository       orderRepository;
    private final ApplicationEventPublisher eventPublisher;

    public OrderApplicationService(OrderRepository orderRepository,
                                   ApplicationEventPublisher eventPublisher) {
        this.orderRepository = orderRepository;
        this.eventPublisher  = eventPublisher;
    }

    // @Transactional: 트랜잭션 경계는 Application Service가 책임
    @Transactional
    public OrderSummaryDto placeOrder(PlaceOrderCommand command) {
        // 1. 도메인 객체 생성 (비즈니스 규칙 검증은 Order.place() 내부에서)
        List<OrderItem> items = command.items().stream()
            .map(dto -> new OrderItem(dto.productId(), dto.quantity(), dto.unitPrice()))
            .collect(Collectors.toList());

        Order order = Order.place(command.customerId(), items); // 도메인 로직 위임

        // 2. 저장
        orderRepository.save(order);

        // 3. 도메인 이벤트 발행 (도메인에서 등록한 이벤트를 Application Service가 발행)
        order.pullDomainEvents().forEach(eventPublisher::publishEvent);

        // 4. 응답 DTO 조립 (도메인 객체를 직접 반환하지 않음)
        return new OrderSummaryDto(
            order.getId(),
            order.getStatus(),
            order.calculateTotal(),
            order.getOrderedAt()
        );
    }

    @Transactional
    public void confirmOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)      // 로드
            .orElseThrow(() -> new IllegalArgumentException("주문 없음: " + orderId));

        order.confirm(); // 도메인 로직 위임 — Application Service는 조율만

        // @Transactional 덕분에 save() 없어도 변경 감지(Dirty Checking)로 저장
    }

    @Transactional(readOnly = true)
    public OrderSummaryDto getOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("주문 없음: " + orderId));
        return new OrderSummaryDto(
            order.getId(), order.getStatus(), order.calculateTotal(), order.getOrderedAt()
        );
    }
}

// ===== [presentation/OrderController.java] =====
package com.example.applicationservice.presentation;

import com.example.applicationservice.application.OrderApplicationService;
import com.example.applicationservice.application.OrderSummaryDto;
import com.example.applicationservice.application.PlaceOrderCommand;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

// Controller: HTTP 변환만 담당, 비즈니스 로직 없음
@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderApplicationService orderService;

    public OrderController(OrderApplicationService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    public ResponseEntity<OrderSummaryDto> place(@RequestBody PlaceOrderCommand command) {
        OrderSummaryDto result = orderService.placeOrder(command); // Application Service에 위임
        return ResponseEntity.ok(result);
    }

    @PatchMapping("/{id}/confirm")
    public ResponseEntity<Void> confirm(@PathVariable Long id) {
        orderService.confirmOrder(id);
        return ResponseEntity.noContent().build();
    }
}""",
        "package_structure": """\
com.example.applicationservice
├── application
│   ├── PlaceOrderCommand.java        ← Command DTO (입력)
│   ├── OrderSummaryDto.java          ← Response DTO (출력)
│   └── OrderApplicationService.java ← 조율 레이어 (핵심)
├── domain
│   ├── Order.java
│   ├── OrderItem.java
│   └── OrderRepository.java
└── presentation
    └── OrderController.java""",
        "key_benefits": [
            "트랜잭션 경계, 이벤트 발행 등 인프라 관심사를 도메인과 분리합니다",
            "얇은 Application Service 덕분에 도메인 로직이 Order 안에 집중됩니다",
            "DTO로 도메인 모델을 외부에 노출하지 않아 API 변경에 유연합니다",
        ],
    },

    "Specification": {
        "pattern_name": "Specification",
        "category": "ddd",
        "overview": "비즈니스 규칙을 독립적인 객체(Specification)로 캡슐화하고, and()/or()/not()으로 조합할 수 있게 하는 패턴입니다. 조건 로직을 재사용 가능한 명시적 객체로 표현합니다.",
        "use_case": "VIP이면서 활성 상태인 고객에게만 특별 쿠폰을 발송하는 조건을 isVip().and(isActive())처럼 도메인 언어로 표현합니다. JPA Specification으로 구현하면 동적 쿼리도 조합 방식으로 처리합니다.",
        "layers_used": ["contract", "domain", "infra"],
        "flow_description": [
            "① CustomerSpecification.isVip()와 isActive()를 각각 독립 Specification으로 정의합니다.",
            "② vipSpec.and(activeSpec)으로 두 조건을 조합한 복합 Specification을 만듭니다.",
            "③ 복합 Specification은 isSatisfiedBy(customer)로 단일 객체를 검증할 수 있습니다.",
            "④ JPA Specification으로 구현하면 customerRepository.findAll(vipAndActive)으로 DB 조회합니다.",
            "⑤ 새 조건 추가 시 기존 Specification을 수정하지 않고 새 클래스를 만들어 조합합니다.",
            "⑥ 비즈니스 규칙이 코드에 명시적으로 드러나 도메인 전문가와 소통이 쉬워집니다."
        ],
        "example_code": """\
// ===== [contract/Specification.java] =====
package com.example.specification.contract;

import org.springframework.data.jpa.domain.Specification;

// 제네릭 Specification 인터페이스: in-memory 검증 + JPA 쿼리 조합 지원
public interface CustomerSpecification<T> {

    boolean isSatisfiedBy(T candidate); // 단일 객체 검증 (비즈니스 규칙 확인)

    Specification<T> toJpaSpec();       // JPA Specification 변환 (DB 조회용)

    // and 조합: 두 조건 모두 만족
    default CustomerSpecification<T> and(CustomerSpecification<T> other) {
        return new AndSpecification<>(this, other);
    }

    // or 조합: 둘 중 하나 만족
    default CustomerSpecification<T> or(CustomerSpecification<T> other) {
        return new OrSpecification<>(this, other);
    }
}

// ===== [domain/Customer.java] =====
package com.example.specification.domain;

import jakarta.persistence.*;
import lombok.Getter;

@Entity
@Getter
public class Customer {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long   id;
    private String name;
    private long   totalPurchaseAmount; // 누적 구매금액
    private String status;              // ACTIVE, INACTIVE, SUSPENDED
    private String grade;               // NORMAL, VIP, VVIP

    protected Customer() {}

    public Customer(String name, long totalPurchaseAmount, String status, String grade) {
        this.name                = name;
        this.totalPurchaseAmount = totalPurchaseAmount;
        this.status              = status;
        this.grade               = grade;
    }
}

// ===== [domain/VipCustomerSpecification.java] =====
package com.example.specification.domain;

import com.example.specification.contract.CustomerSpecification;
import org.springframework.data.jpa.domain.Specification;

// VIP 고객 조건: 등급이 VIP 이상이거나 누적 구매 100만원 이상
public class VipCustomerSpecification implements CustomerSpecification<Customer> {

    private static final long VIP_THRESHOLD = 1_000_000L;

    @Override
    public boolean isSatisfiedBy(Customer customer) {
        return "VIP".equals(customer.getGrade()) || "VVIP".equals(customer.getGrade())
            || customer.getTotalPurchaseAmount() >= VIP_THRESHOLD;
    }

    @Override
    public Specification<Customer> toJpaSpec() {
        // JPA Specification: WHERE (grade IN ('VIP','VVIP') OR totalPurchaseAmount >= 1000000)
        return (root, query, cb) -> cb.or(
            root.get("grade").in("VIP", "VVIP"),
            cb.greaterThanOrEqualTo(root.get("totalPurchaseAmount"), VIP_THRESHOLD)
        );
    }
}

// ===== [domain/ActiveCustomerSpecification.java] =====
package com.example.specification.domain;

import com.example.specification.contract.CustomerSpecification;
import org.springframework.data.jpa.domain.Specification;

// 활성 고객 조건: 상태가 ACTIVE인 고객
public class ActiveCustomerSpecification implements CustomerSpecification<Customer> {

    @Override
    public boolean isSatisfiedBy(Customer customer) {
        return "ACTIVE".equals(customer.getStatus());
    }

    @Override
    public Specification<Customer> toJpaSpec() {
        return (root, query, cb) -> cb.equal(root.get("status"), "ACTIVE");
    }
}

// ===== [contract/AndSpecification.java] =====
package com.example.specification.contract;

import org.springframework.data.jpa.domain.Specification;

// 조합 Specification: 두 조건 모두 충족
public class AndSpecification<T> implements CustomerSpecification<T> {

    private final CustomerSpecification<T> left;
    private final CustomerSpecification<T> right;

    public AndSpecification(CustomerSpecification<T> left, CustomerSpecification<T> right) {
        this.left  = left;
        this.right = right;
    }

    @Override
    public boolean isSatisfiedBy(T candidate) {
        return left.isSatisfiedBy(candidate) && right.isSatisfiedBy(candidate);
    }

    @Override
    public Specification<T> toJpaSpec() {
        return left.toJpaSpec().and(right.toJpaSpec()); // JPA Specification 조합
    }
}

// ===== [infra/CustomerRepositoryImpl.java 사용 예시] =====
package com.example.specification.infra;

import com.example.specification.domain.*;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class VipCouponService {

    private final CustomerJpaRepository customerRepository;

    public VipCouponService(CustomerJpaRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    public List<Customer> findVipActiveCustomers() {
        // Specification 조합: 도메인 언어로 조건 표현
        var vipSpec    = new VipCustomerSpecification();
        var activeSpec = new ActiveCustomerSpecification();
        var combined   = vipSpec.and(activeSpec); // VIP이면서 활성 상태

        // JPA Specification으로 DB 조회
        return customerRepository.findAll(combined.toJpaSpec());
    }
}""",
        "package_structure": """\
com.example.specification
├── contract
│   ├── CustomerSpecification.java  ← 인터페이스 (and/or 조합 기본 메서드)
│   ├── AndSpecification.java
│   └── OrSpecification.java
├── domain
│   ├── Customer.java
│   ├── VipCustomerSpecification.java    ← 비즈니스 규칙 객체
│   └── ActiveCustomerSpecification.java ← 비즈니스 규칙 객체
└── infra
    └── VipCouponService.java""",
        "key_benefits": [
            "비즈니스 규칙을 명시적인 객체로 표현하여 도메인 전문가와 소통이 쉬워집니다",
            "and()/or()로 복잡한 조건을 조합해도 각 규칙은 단독으로 테스트 가능합니다",
            "isSatisfiedBy()로 메모리 검증, toJpaSpec()으로 DB 쿼리를 동일한 규칙으로 처리합니다",
        ],
    },

    "CQRS": {
        "pattern_name": "CQRS",
        "category": "ddd",
        "overview": "Command(쓰기)와 Query(읽기) 모델을 분리하는 패턴입니다. 쓰기 모델은 도메인 로직과 불변식 보호에 집중하고, 읽기 모델은 UI에 최적화된 데이터를 빠르게 반환합니다.",
        "use_case": "주문 생성(Command)과 주문 목록 조회(Query)를 분리합니다. Command는 도메인 모델을 거쳐 처리하고, Query는 복잡한 JOIN 쿼리를 직접 실행합니다. 읽기 DB를 분리하거나 읽기 모델 캐싱도 가능합니다.",
        "layers_used": ["contract", "application", "infra", "presentation"],
        "flow_description": [
            "① OrderCommandController가 OrderCreateCommand를 받아 OrderCommandService.createOrder()를 호출합니다.",
            "② OrderCommandService는 도메인 모델(Order)을 생성하고 저장합니다 (쓰기 최적화).",
            "③ OrderQueryController가 목록 조회 요청을 받아 OrderQueryService.getOrderList()를 호출합니다.",
            "④ OrderQueryService는 도메인 모델을 거치지 않고 DB에서 OrderSummaryDto를 직접 조회합니다.",
            "⑤ 읽기 모델(OrderSummaryDto)은 여러 테이블을 JOIN하거나 캐시에서 반환할 수 있습니다.",
            "⑥ 쓰기와 읽기 처리량이 달라도 독립적으로 스케일 아웃 가능합니다."
        ],
        "example_code": """\
// ===== [contract/OrderCreateCommand.java] =====
package com.example.cqrs.contract;

import java.util.List;

// Command: 쓰기 작업의 입력 DTO — 의도가 명확한 이름 사용
public record OrderCreateCommand(
    String        customerId,
    List<ItemDto> items
) {
    public record ItemDto(String productId, int quantity, long unitPrice) {}
}

// ===== [contract/OrderSummaryDto.java] =====
package com.example.cqrs.contract;

import java.time.LocalDateTime;

// Query: 읽기 모델 — UI 최적화, 여러 테이블 데이터 조합 가능
public record OrderSummaryDto(
    Long          orderId,
    String        customerName,  // Customer 테이블 JOIN
    String        status,
    long          totalAmount,
    int           itemCount,     // 집계 값
    LocalDateTime orderedAt
) {}

// ===== [application/OrderCommandService.java] =====
package com.example.cqrs.application;

import com.example.cqrs.contract.OrderCreateCommand;
import com.example.cqrs.domain.Order;
import com.example.cqrs.domain.OrderItem;
import com.example.cqrs.domain.OrderRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.stream.Collectors;

// Command Service: 쓰기 전용 — 도메인 모델로 불변식 보호
@Service
public class OrderCommandService {

    private final OrderRepository orderRepository;

    public OrderCommandService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @Transactional
    public Long createOrder(OrderCreateCommand command) {
        var items = command.items().stream()
            .map(dto -> new OrderItem(dto.productId(), dto.quantity(), dto.unitPrice()))
            .collect(Collectors.toList());

        Order order = Order.place(command.customerId(), items); // 도메인 불변식 검증
        orderRepository.save(order);
        System.out.println("[Command] 주문 생성: " + order.getId());
        return order.getId();
    }

    @Transactional
    public void cancelOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("주문 없음: " + orderId));
        order.cancel(); // 도메인 로직 — 취소 가능 여부 검증 포함
    }
}

// ===== [application/OrderQueryService.java] =====
package com.example.cqrs.application;

import com.example.cqrs.contract.OrderSummaryDto;
import com.example.cqrs.infra.OrderQueryRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

// Query Service: 읽기 전용 — 도메인 모델 거치지 않고 최적화된 조회
@Service
@Transactional(readOnly = true) // 읽기 전용 트랜잭션 — 성능 최적화
public class OrderQueryService {

    private final OrderQueryRepository queryRepository; // 읽기 전용 Repository

    public OrderQueryService(OrderQueryRepository queryRepository) {
        this.queryRepository = queryRepository;
    }

    public List<OrderSummaryDto> getOrderList(String customerId) {
        // 도메인 모델을 로드하지 않고 DTO를 직접 조회 (N+1 문제 방지)
        return queryRepository.findOrderSummariesByCustomerId(customerId);
    }

    public OrderSummaryDto getOrderDetail(Long orderId) {
        return queryRepository.findOrderSummaryById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("주문 없음: " + orderId));
    }
}

// ===== [infra/OrderQueryRepository.java] =====
package com.example.cqrs.infra;

import com.example.cqrs.contract.OrderSummaryDto;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

// 읽기 전용 Repository: JOIN + 집계 쿼리 최적화
public interface OrderQueryRepository extends JpaRepository<com.example.cqrs.domain.Order, Long> {

    // JPQL: Customer JOIN하여 customerName 포함, itemCount 집계
    @Query("""
        SELECT new com.example.cqrs.contract.OrderSummaryDto(
            o.id, c.name, o.status, o.totalAmount, SIZE(o.items), o.orderedAt
        )
        FROM Order o JOIN Customer c ON o.customerId = c.id
        WHERE o.customerId = :customerId
        ORDER BY o.orderedAt DESC
        """)
    List<OrderSummaryDto> findOrderSummariesByCustomerId(String customerId);

    @Query("""
        SELECT new com.example.cqrs.contract.OrderSummaryDto(
            o.id, c.name, o.status, o.totalAmount, SIZE(o.items), o.orderedAt
        )
        FROM Order o JOIN Customer c ON o.customerId = c.id
        WHERE o.id = :orderId
        """)
    Optional<OrderSummaryDto> findOrderSummaryById(Long orderId);
}

// ===== [presentation/OrderController.java] =====
package com.example.cqrs.presentation;

import com.example.cqrs.application.OrderCommandService;
import com.example.cqrs.application.OrderQueryService;
import com.example.cqrs.contract.OrderCreateCommand;
import com.example.cqrs.contract.OrderSummaryDto;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderCommandService commandService; // 쓰기 전용
    private final OrderQueryService   queryService;   // 읽기 전용

    public OrderController(OrderCommandService commandService, OrderQueryService queryService) {
        this.commandService = commandService;
        this.queryService   = queryService;
    }

    @PostMapping  // Command: 쓰기
    public ResponseEntity<Long> create(@RequestBody OrderCreateCommand command) {
        return ResponseEntity.ok(commandService.createOrder(command));
    }

    @GetMapping("/customer/{customerId}")  // Query: 읽기
    public ResponseEntity<List<OrderSummaryDto>> list(@PathVariable String customerId) {
        return ResponseEntity.ok(queryService.getOrderList(customerId));
    }
}""",
        "package_structure": """\
com.example.cqrs
├── contract
│   ├── OrderCreateCommand.java  ← Command 입력 DTO
│   └── OrderSummaryDto.java     ← Query 출력 DTO
├── application
│   ├── OrderCommandService.java ← 쓰기 전용 서비스
│   └── OrderQueryService.java   ← 읽기 전용 서비스
├── domain
│   ├── Order.java
│   └── OrderRepository.java
├── infra
│   └── OrderQueryRepository.java ← 읽기 최적화 쿼리
└── presentation
    └── OrderController.java""",
        "key_benefits": [
            "쓰기와 읽기 모델 분리로 각각 독립적으로 최적화하고 스케일 아웃할 수 있습니다",
            "읽기 모델은 도메인 모델을 거치지 않아 JOIN/집계 쿼리를 자유롭게 사용합니다",
            "Command는 도메인 불변식을 보호하고, Query는 UI 요구사항에 직접 최적화됩니다",
        ],
    },

    "Event Sourcing": {
        "pattern_name": "Event Sourcing",
        "category": "ddd",
        "overview": "엔티티의 현재 상태를 직접 저장하는 대신 상태를 변경한 모든 이벤트를 순서대로 저장하는 패턴입니다. 이벤트를 재생(replay)하여 언제든지 과거 상태를 복원할 수 있습니다.",
        "use_case": "BankAccount(은행 계좌)의 현재 잔액 대신 AccountOpened, MoneyDeposited, MoneyWithdrawn 이벤트를 EventStore에 저장합니다. 잔액 조회 시 모든 이벤트를 재생하여 계산합니다. 완전한 감사 로그와 상태 복원이 가능합니다.",
        "layers_used": ["domain", "infra", "application"],
        "flow_description": [
            "① BankAccount.open(accountId, ownerId)이 AccountOpenedEvent를 생성하고 내부 이벤트 목록에 추가합니다.",
            "② deposit()/withdraw() 호출 시 각각 MoneyDepositedEvent, MoneyWithdrawnEvent가 등록됩니다.",
            "③ EventStore.save()가 등록된 이벤트들을 event_store 테이블에 순서대로 저장합니다.",
            "④ 계좌 조회 시 EventStore.load(accountId)로 모든 이벤트를 로드합니다.",
            "⑤ BankAccount.reconstitute()가 이벤트를 순서대로 재생하여 현재 잔액을 복원합니다.",
            "⑥ 특정 시점의 상태 조회는 해당 시점까지의 이벤트만 재생하면 됩니다.",
            "⑦ 이벤트 로그 자체가 완전한 감사 추적(Audit Trail)이 됩니다."
        ],
        "example_code": """\
// ===== [domain/DomainEvent.java] =====
package com.example.eventsourcing.domain;

import java.time.LocalDateTime;
import java.util.UUID;

// 모든 도메인 이벤트의 기반 클래스
public abstract class DomainEvent {
    private final String        eventId;      // 이벤트 고유 ID
    private final String        aggregateId;  // 어떤 Aggregate의 이벤트인지
    private final LocalDateTime occurredAt;   // 발생 시각
    private final int           version;      // 이벤트 순서 번호

    protected DomainEvent(String aggregateId, int version) {
        this.eventId     = UUID.randomUUID().toString();
        this.aggregateId = aggregateId;
        this.occurredAt  = LocalDateTime.now();
        this.version     = version;
    }

    public String        getEventId()     { return eventId; }
    public String        getAggregateId() { return aggregateId; }
    public LocalDateTime getOccurredAt()  { return occurredAt; }
    public int           getVersion()     { return version; }
    public abstract String getEventType();
}

// ===== [domain/AccountOpenedEvent.java] =====
package com.example.eventsourcing.domain;

import lombok.Getter;

@Getter
public class AccountOpenedEvent extends DomainEvent {
    private final String ownerId;
    private final long   initialBalance;

    public AccountOpenedEvent(String aggregateId, int version, String ownerId, long initialBalance) {
        super(aggregateId, version);
        this.ownerId        = ownerId;
        this.initialBalance = initialBalance;
    }

    @Override public String getEventType() { return "ACCOUNT_OPENED"; }
}

// ===== [domain/MoneyDepositedEvent.java] =====
package com.example.eventsourcing.domain;

import lombok.Getter;

@Getter
public class MoneyDepositedEvent extends DomainEvent {
    private final long amount;

    public MoneyDepositedEvent(String aggregateId, int version, long amount) {
        super(aggregateId, version);
        this.amount = amount;
    }

    @Override public String getEventType() { return "MONEY_DEPOSITED"; }
}

// ===== [domain/MoneyWithdrawnEvent.java] =====
package com.example.eventsourcing.domain;

import lombok.Getter;

@Getter
public class MoneyWithdrawnEvent extends DomainEvent {
    private final long amount;

    public MoneyWithdrawnEvent(String aggregateId, int version, long amount) {
        super(aggregateId, version);
        this.amount = amount;
    }

    @Override public String getEventType() { return "MONEY_WITHDRAWN"; }
}

// ===== [domain/BankAccount.java] =====
package com.example.eventsourcing.domain;

import java.util.ArrayList;
import java.util.List;

// Event Sourcing Aggregate: 현재 상태 대신 이벤트로 관리
public class BankAccount {

    private String accountId;
    private String ownerId;
    private long   balance;    // 이벤트 재생으로 복원되는 잔액
    private int    version;    // 현재 이벤트 버전 (낙관적 동시성 제어)

    // 미저장 신규 이벤트 목록
    private final List<DomainEvent> pendingEvents = new ArrayList<>();

    private BankAccount() {} // 외부 직접 생성 불가 — 팩토리 또는 reconstitute 사용

    // 신규 계좌 개설: 이벤트 생성 후 내부 apply()로 상태 갱신
    public static BankAccount open(String accountId, String ownerId, long initialBalance) {
        BankAccount account = new BankAccount();
        account.apply(new AccountOpenedEvent(accountId, 1, ownerId, initialBalance));
        return account;
    }

    public void deposit(long amount) {
        if (amount <= 0) throw new IllegalArgumentException("입금액은 0보다 커야 합니다");
        apply(new MoneyDepositedEvent(accountId, version + 1, amount));
    }

    public void withdraw(long amount) {
        if (amount <= 0)    throw new IllegalArgumentException("출금액은 0보다 커야 합니다");
        if (balance < amount) throw new IllegalStateException("잔액 부족: " + balance);
        apply(new MoneyWithdrawnEvent(accountId, version + 1, amount));
    }

    // 이벤트 적용: 상태 변경 + 신규 이벤트 목록에 추가
    private void apply(DomainEvent event) {
        handle(event);              // 상태 변경
        pendingEvents.add(event);   // 저장 대기 목록에 추가
    }

    // 이벤트 타입별 상태 변경 처리 (재생할 때도 사용)
    private void handle(DomainEvent event) {
        if (event instanceof AccountOpenedEvent e) {
            this.accountId = e.getAggregateId();
            this.ownerId   = e.getOwnerId();
            this.balance   = e.getInitialBalance();
            this.version   = e.getVersion();
        } else if (event instanceof MoneyDepositedEvent e) {
            this.balance += e.getAmount(); // 입금: 잔액 증가
            this.version  = e.getVersion();
        } else if (event instanceof MoneyWithdrawnEvent e) {
            this.balance -= e.getAmount(); // 출금: 잔액 감소
            this.version  = e.getVersion();
        }
    }

    // 이벤트 재생으로 과거 상태 복원 (EventStore에서 로드할 때 사용)
    public static BankAccount reconstitute(List<DomainEvent> events) {
        BankAccount account = new BankAccount();
        for (DomainEvent event : events) {
            account.handle(event); // 순서대로 재생
        }
        return account;
    }

    public List<DomainEvent> pullPendingEvents() {
        List<DomainEvent> events = new ArrayList<>(pendingEvents);
        pendingEvents.clear();
        return events;
    }

    public String getAccountId() { return accountId; }
    public String getOwnerId()   { return ownerId; }
    public long   getBalance()   { return balance; }
    public int    getVersion()   { return version; }
}

// ===== [infra/EventStore.java] =====
package com.example.eventsourcing.infra;

import com.example.eventsourcing.domain.DomainEvent;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

// EventStore: 이벤트를 순서대로 저장하고 로드
@Repository
public class EventStore {

    private final JdbcTemplate jdbcTemplate;

    public EventStore(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    // 이벤트 저장 (append-only: 수정/삭제 없음)
    public void save(List<DomainEvent> events) {
        for (DomainEvent event : events) {
            jdbcTemplate.update(
                "INSERT INTO event_store (event_id, aggregate_id, event_type, version, occurred_at) VALUES (?,?,?,?,?)",
                event.getEventId(), event.getAggregateId(),
                event.getEventType(), event.getVersion(), event.getOccurredAt()
            );
            System.out.println("[EventStore] 저장: " + event.getEventType() + " v" + event.getVersion());
        }
    }
}

// ===== [application/BankAccountService.java] =====
package com.example.eventsourcing.application;

import com.example.eventsourcing.domain.BankAccount;
import com.example.eventsourcing.infra.EventStore;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class BankAccountService {

    private final EventStore eventStore;

    public BankAccountService(EventStore eventStore) {
        this.eventStore = eventStore;
    }

    @Transactional
    public BankAccount openAccount(String accountId, String ownerId, long initialBalance) {
        BankAccount account = BankAccount.open(accountId, ownerId, initialBalance);
        eventStore.save(account.pullPendingEvents()); // 이벤트 저장
        return account;
    }

    @Transactional
    public void deposit(String accountId, long amount) {
        // 실제 구현: EventStore에서 이벤트 로드 후 reconstitute
        System.out.println("[입금] 계좌: " + accountId + ", 금액: " + amount);
    }
}""",
        "package_structure": """\
com.example.eventsourcing
├── domain
│   ├── DomainEvent.java           ← 이벤트 기반 클래스
│   ├── AccountOpenedEvent.java
│   ├── MoneyDepositedEvent.java
│   ├── MoneyWithdrawnEvent.java
│   └── BankAccount.java           ← Event Sourcing Aggregate
├── infra
│   └── EventStore.java            ← Append-only 이벤트 저장소
└── application
    └── BankAccountService.java""",
        "key_benefits": [
            "모든 상태 변경이 이벤트로 기록되어 완전한 감사 로그(Audit Trail)가 자동 생성됩니다",
            "과거 임의 시점의 상태를 이벤트 재생으로 정확히 복원할 수 있습니다",
            "이벤트 스트림을 통해 다양한 읽기 모델(CQRS)을 생성하거나 이벤트 재처리가 가능합니다",
        ],
    },

    "Saga": {
        "pattern_name": "Saga",
        "category": "ddd",
        "overview": "여러 서비스에 걸친 분산 트랜잭션을 일련의 로컬 트랜잭션과 보상 트랜잭션(Compensating Transaction)으로 처리하는 패턴입니다. 각 서비스는 성공/실패 이벤트를 발행하여 다음 단계를 트리거합니다.",
        "use_case": "주문(Order) → 재고 예약(Inventory) → 결제(Payment) 흐름에서 결제 실패 시 재고를 되돌리는 보상 트랜잭션을 구현합니다. 코레오그래피(Choreography) 방식으로 각 서비스가 이벤트를 수신하여 자율적으로 처리합니다.",
        "layers_used": ["application", "domain"],
        "flow_description": [
            "① OrderService가 주문을 생성하고 OrderPlacedEvent를 발행합니다.",
            "② InventoryService가 OrderPlacedEvent를 받아 재고를 예약하고 InventoryReservedEvent를 발행합니다.",
            "③ PaymentService가 InventoryReservedEvent를 받아 결제를 처리하고 PaymentProcessedEvent를 발행합니다.",
            "④ 결제 실패 시 PaymentFailedEvent를 발행합니다.",
            "⑤ InventoryService가 PaymentFailedEvent를 받아 재고 예약을 해제합니다 (보상 트랜잭션).",
            "⑥ OrderService가 PaymentFailedEvent를 받아 주문을 취소합니다 (보상 트랜잭션).",
            "⑦ 각 서비스는 독립 트랜잭션으로 처리 — 분산 트랜잭션 없이 최종 일관성을 달성합니다."
        ],
        "example_code": """\
// ===== [domain/OrderPlacedEvent.java] =====
package com.example.saga.domain;

import lombok.Getter;
import org.springframework.context.ApplicationEvent;

// Saga 시작 이벤트: 주문 접수
@Getter
public class OrderPlacedEvent extends ApplicationEvent {
    private final String orderId;
    private final String customerId;
    private final String productId;
    private final int    quantity;

    public OrderPlacedEvent(Object src, String orderId, String customerId,
                            String productId, int quantity) {
        super(src);
        this.orderId    = orderId;
        this.customerId = customerId;
        this.productId  = productId;
        this.quantity   = quantity;
    }
}

// ===== [domain/InventoryReservedEvent.java] =====
package com.example.saga.domain;

import lombok.Getter;
import org.springframework.context.ApplicationEvent;

// 재고 예약 성공 이벤트
@Getter
public class InventoryReservedEvent extends ApplicationEvent {
    private final String orderId;
    private final String productId;
    private final int    quantity;

    public InventoryReservedEvent(Object src, String orderId, String productId, int quantity) {
        super(src);
        this.orderId   = orderId;
        this.productId = productId;
        this.quantity  = quantity;
    }
}

// ===== [domain/PaymentFailedEvent.java] =====
package com.example.saga.domain;

import lombok.Getter;
import org.springframework.context.ApplicationEvent;

// 결제 실패 이벤트: 보상 트랜잭션 트리거
@Getter
public class PaymentFailedEvent extends ApplicationEvent {
    private final String orderId;
    private final String reason;

    public PaymentFailedEvent(Object src, String orderId, String reason) {
        super(src);
        this.orderId = orderId;
        this.reason  = reason;
    }
}

// ===== [application/OrderService.java] =====
package com.example.saga.application;

import com.example.saga.domain.*;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// Saga 참여자 1: 주문 서비스
@Service
public class OrderService {

    private final ApplicationEventPublisher eventPublisher;

    public OrderService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    // Saga 시작: 주문 생성 후 이벤트 발행
    @Transactional
    public void placeOrder(String customerId, String productId, int quantity) {
        String orderId = "ORD-" + System.currentTimeMillis();
        System.out.println("[Order] 주문 생성: " + orderId);
        // DB에 PENDING 상태로 저장

        // 다음 Saga 참여자에게 이벤트로 알림
        eventPublisher.publishEvent(
            new OrderPlacedEvent(this, orderId, customerId, productId, quantity)
        );
    }

    // 보상 트랜잭션: 결제 실패 시 주문 취소
    @EventListener
    @Transactional
    public void onPaymentFailed(PaymentFailedEvent event) {
        System.out.println("[Order] 보상 트랜잭션 실행 — 주문 취소: " + event.getOrderId()
            + " 사유: " + event.getReason());
        // DB에서 해당 주문을 CANCELLED로 업데이트
    }
}

// ===== [application/InventoryService.java] =====
package com.example.saga.application;

import com.example.saga.domain.*;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// Saga 참여자 2: 재고 서비스
@Service
public class InventoryService {

    private final ApplicationEventPublisher eventPublisher;

    public InventoryService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    // 주문 이벤트 수신 → 재고 예약 → 다음 이벤트 발행
    @EventListener
    @Transactional
    public void onOrderPlaced(OrderPlacedEvent event) {
        System.out.println("[Inventory] 재고 예약 시도: " + event.getProductId()
            + " x" + event.getQuantity());

        boolean reserved = reserveStock(event.getProductId(), event.getQuantity());

        if (reserved) {
            System.out.println("[Inventory] 재고 예약 성공");
            eventPublisher.publishEvent(
                new InventoryReservedEvent(this, event.getOrderId(),
                                           event.getProductId(), event.getQuantity())
            );
        } else {
            System.out.println("[Inventory] 재고 부족 — Saga 실패 처리");
            eventPublisher.publishEvent(
                new PaymentFailedEvent(this, event.getOrderId(), "재고 부족")
            );
        }
    }

    // 보상 트랜잭션: 결제 실패 시 재고 예약 해제
    @EventListener
    @Transactional
    public void onPaymentFailed(PaymentFailedEvent event) {
        System.out.println("[Inventory] 보상 트랜잭션 — 재고 예약 해제: " + event.getOrderId());
        // DB에서 해당 주문의 재고 예약 레코드 삭제
    }

    private boolean reserveStock(String productId, int quantity) {
        // 실제: 재고 DB 조회 및 예약 처리
        return true; // 시뮬레이션: 성공
    }
}

// ===== [application/PaymentService.java] =====
package com.example.saga.application;

import com.example.saga.domain.*;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// Saga 참여자 3: 결제 서비스
@Service
public class PaymentService {

    private final ApplicationEventPublisher eventPublisher;

    public PaymentService(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    // 재고 예약 이벤트 수신 → 결제 처리
    @EventListener
    @Transactional
    public void onInventoryReserved(InventoryReservedEvent event) {
        System.out.println("[Payment] 결제 처리 시도: 주문 " + event.getOrderId());

        boolean paid = processPayment(event.getOrderId());

        if (paid) {
            System.out.println("[Payment] 결제 성공 — Saga 완료");
            // PaymentProcessedEvent 발행으로 주문 CONFIRMED 처리
        } else {
            System.out.println("[Payment] 결제 실패 — 보상 트랜잭션 시작");
            // 결제 실패 이벤트 발행 → Inventory/Order 보상 트랜잭션 트리거
            eventPublisher.publishEvent(
                new PaymentFailedEvent(this, event.getOrderId(), "카드 한도 초과")
            );
        }
    }

    private boolean processPayment(String orderId) {
        // 실제: 결제 게이트웨이 호출
        return true; // 시뮬레이션: 성공
    }
}""",
        "package_structure": """\
com.example.saga
├── domain
│   ├── OrderPlacedEvent.java       ← Saga 시작 이벤트
│   ├── InventoryReservedEvent.java ← 재고 예약 완료
│   └── PaymentFailedEvent.java     ← 보상 트랜잭션 트리거
└── application
    ├── OrderService.java      ← Saga 참여자 1 (시작 + 보상)
    ├── InventoryService.java  ← Saga 참여자 2 (예약 + 보상)
    └── PaymentService.java    ← Saga 참여자 3 (결제)""",
        "key_benefits": [
            "분산 트랜잭션(2PC) 없이 여러 서비스에 걸친 비즈니스 프로세스를 관리합니다",
            "각 서비스는 독립 트랜잭션으로 처리하여 서비스 간 결합도를 낮춥니다",
            "보상 트랜잭션으로 실패 시 최종 일관성(Eventual Consistency)을 달성합니다",
        ],
    },
}
