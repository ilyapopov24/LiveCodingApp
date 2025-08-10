# System Patterns: LiveCodingApp

## Architecture Overview

### Clean Architecture Implementation
The application follows Clean Architecture principles with three distinct layers:

```
┌─────────────────────────────────────┐
│           Presentation              │
│  (UI, ViewModels, Activities)      │
├─────────────────────────────────────┤
│             Domain                  │
│  (Entities, Use Cases, Repository) │
├─────────────────────────────────────┤
│              Data                   │
│  (API, Database, Mappers)          │
└─────────────────────────────────────┘
```

### Layer Responsibilities

#### **Presentation Layer** (`presentation/`)
- **UI Components**: Activities, Fragments, Adapters
- **ViewModels**: Business logic for UI, LiveData management
- **Data Binding**: ViewBinding for efficient UI updates
- **Navigation**: Fragment-based navigation within MainActivity

#### **Domain Layer** (`domain/`)
- **Entities**: Pure Kotlin data classes representing business objects
- **Repository Interfaces**: Contracts defining data access methods
- **Use Cases**: Business logic orchestration (currently minimal)

#### **Data Layer** (`data/`)
- **API Integration**: Retrofit-based network calls
- **Local Storage**: Room database for offline caching
- **Mappers**: Data transformation between layers
- **Repository Implementation**: Concrete repository classes

## Design Patterns

### **MVVM (Model-View-ViewModel)**
- **View**: Activities and Fragments observe ViewModels
- **ViewModel**: Manages UI state and business logic
- **Model**: Domain entities and repository data

### **Repository Pattern**
```kotlin
interface CharactersRepository {
    fun getContent(): LiveData<ContentEntity>
    suspend fun loadPage(page: Int)
}
```
- **Abstraction**: UI doesn't know about data sources
- **Single Source of Truth**: Repository manages data flow
- **Offline-First**: Local database as primary data source

### **Mapper Pattern**
```kotlin
interface ContentMapper {
    fun mapToEntity(dto: Content): ContentEntity
}

interface DBMapper {
    fun mapToEntity(dbModel: CharactersDBModel): ContentEntity
}
```
- **Data Transformation**: Clean separation between data formats
- **Type Safety**: Compile-time validation of mappings
- **Testability**: Isolated mapping logic for unit testing

### **Dependency Injection (Hilt)**
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    fun provideRetrofit(): Retrofit
}
```
- **Singleton Management**: Network and database instances
- **Testability**: Easy mock injection for testing
- **Lifecycle Management**: Proper scoping of dependencies

## Data Flow Patterns

### **API to UI Data Flow**
```
API Response → DTO → Mapper → Entity → Repository → ViewModel → LiveData → UI
```

### **Pagination Pattern**
```kotlin
fun onPageFinished() = viewModelScope.launch(Dispatchers.IO) {
    repo.loadPage(++page)
}
```
- **Incremental Loading**: Page-based data fetching
- **Background Processing**: IO dispatcher for network calls
- **State Management**: Page counter in ViewModel

### **Caching Strategy**
```
Network Request → Local Database → UI Update
     ↓
Offline Access ← Local Database ← UI Request
```
- **Write-Through**: Data immediately cached after API response
- **Read-From-Cache**: UI always reads from local database
- **Background Sync**: Repository manages data freshness

## Component Relationships

### **Module Dependencies**
```
app (UI) → domain (Entities, Repository Interfaces)
data (Implementation) → domain (Repository Interfaces)
app (DI) → data (Concrete Classes)
```

### **Data Binding Chain**
```
CharactersViewModel → CharactersRepository → CharactersRepositoryImpl
     ↓
LiveData<ContentEntity> → CharactersAdapter → RecyclerView
```

### **Fragment Management**
```
MainActivity → CharactersListFragment → CharactersAdapter
     ↓
CharactersViewModel (Shared ViewModel)
```

## Technical Decisions

### **Kotlin-First Approach**
- **Data Classes**: Immutable data structures
- **Coroutines**: Asynchronous programming with structured concurrency
- **Extension Functions**: Utility methods for common operations
- **Null Safety**: Kotlin's type system for null safety

### **Modern Android Architecture Components**
- **LiveData**: Observable data holder with lifecycle awareness
- **ViewModel**: UI state management and lifecycle handling
- **Room**: Local database with compile-time verification
- **ViewBinding**: Type-safe view access

### **Network Architecture**
- **Retrofit**: Type-safe HTTP client
- **GSON**: JSON serialization/deserialization
- **Base URL**: https://rickandmortyapi.com/
- **RESTful API**: Standard HTTP methods and status codes

### **Database Design**
- **Room Database**: SQLite abstraction with compile-time verification
- **DAO Pattern**: Data Access Objects for database operations
- **Type Converters**: Custom serialization for complex types
- **Migration Support**: Database schema evolution

## Error Handling Patterns

### **Current Implementation**
- **Basic Error Handling**: Minimal error state management
- **Silent Failures**: Errors don't propagate to UI
- **No Retry Logic**: Failed requests aren't retried

### **Future Improvements Needed**
- **Error States**: Loading, success, error, empty states
- **Retry Mechanisms**: Automatic and manual retry options
- **User Feedback**: Toast messages, error dialogs
- **Offline Indicators**: Clear offline status communication

## Performance Patterns

### **Memory Management**
- **Pagination**: Prevents memory overflow with large datasets
- **Image Loading**: Efficient image handling (to be implemented)
- **RecyclerView**: Efficient list rendering with view recycling

### **Background Processing**
- **Coroutines**: Non-blocking UI operations
- **IO Dispatcher**: Network and database operations
- **Main Dispatcher**: UI updates and user interactions

## Testing Patterns

### **Current Testing Structure**
- **Unit Tests**: Basic test files in each module
- **Instrumented Tests**: Android-specific testing setup
- **Test Dependencies**: JUnit and Android testing libraries

### **Testing Strategy Needed**
- **Repository Testing**: Mock API and database
- **ViewModel Testing**: Business logic validation
- **UI Testing**: User interaction validation
- **Integration Testing**: End-to-end workflow testing

This system patterns document provides the architectural foundation for understanding how all components interact and how the application maintains clean separation of concerns while delivering a responsive user experience.
