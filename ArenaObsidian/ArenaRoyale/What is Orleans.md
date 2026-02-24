---

tags: [orleans, concept, fundamental]

created: 2026-02-17

---
# What is Orleans?


**Orleans** is a cross-platform framework by Microsoft for building distributed, scalable applications using the **Virtual Actor Model** in .NET.

## Key Ideas

- Simplifies distributed systems – you write single-server code, Orleans handles distribution
- Originally built by Microsoft Research for **Halo** backend services
- Now open-source, used in Xbox, Azure, Skype, and many game backends

## How it differs from traditional approaches

| Traditional                            | Orleans                                          |
| -------------------------------------- | ------------------------------------------------ |
| You manage threads, locks, concurrency | Orleans manages it for you                       |
| You decide where state lives           | Grains are location-transparent                  |
| Explicit lifecycle management          | Virtual actors activate/deactivate automatically |
| Manual scaling decisions               | Automatic grain placement across silos           |
  
## Core Building Blocks

- **[[Grains]]** – the virtual actors (stateful objects with identity)
- **[[Silos]]** – the hosts that run grains
- **[[Clusters]]** – groups of silos working together

## Links

- [[Virtual Actor Model]]
- [[Grain Lifecycle]]
- [Official Docs](https://learn.microsoft.com/en-us/dotnet/orleans/)
