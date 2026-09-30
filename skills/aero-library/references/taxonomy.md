# Logical library taxonomy

Keep plugin instructions, collected material, and AERO engineering records separate.
This taxonomy describes output organization; create only categories that have content.
No SQL database, object store, vector index, or journal service is implied.

Top-level entities:
- devices/game_consoles/<manufacturer>/<platform> and variants/<variant>
- devices/peripherals/<manufacturer>/<peripheral> and devices/arcade_systems/<platform>
- games/<game>/releases/<release>, mods_and_modpacks, ports_and_reimplementations
- software_projects/<project>/releases/<version-or-unknown>
- online_services/<service>
- shared_knowledge/<topic>

Per-device categories:
identity: names_aliases, models_and_regions, release_history, compatibility_relationships.
hardware: architecture_overviews, cpu_isa_abi, gpu_graphics, dsp_audio,
memory_and_address_maps, buses_interfaces_io, storage_and_media,
boot_and_security_architecture, boards_chips_revisions, schematics_pinouts,
power_thermal, teardown_repair.
system_firmware: releases, components, update_and_recovery_formats,
installation_dependencies, custom_distributions, unknown_or_unattributed.
system_software: menus_shells, system_applications, runtime_services,
drivers_modules, diagnostics_recovery, configuration_data.
sdks_and_toolchains: official_sdk_references, community_sdks,
compilers_assemblers_linkers, debuggers_profilers, build_systems, build_environment_recipes.
system_libraries: shared project/release references, not duplicated code snapshots.
development: api_abi_reference, graphics_audio_input, storage_filesystem_apis,
networking_apis, examples_and_test_programs, packaging_deployment.
formats: executables_and_objects, archives_compression, filesystems_disc_cartridge_images,
saves_configuration, graphics_audio_video_assets, installation_update_packages.
networking: hardware_and_adapters, protocols_message_formats, discovery_matchmaking,
account_authentication_reference, service_dependencies, packet_capture_references,
original_services, community_replacement_services, server_hosting_requirements.
reverse_engineering: research_publications, source_recovery_projects,
decompilation_projects, disassembly_and_symbols, static_analysis,
dynamic_analysis_and_traces, hardware_measurement_references,
contradictions_open_questions.
emulation_and_reimplementation: emulator_projects, subsystem_reimplementations,
compatibility_reports, accuracy_test_suites.
homebrew: applications_utilities, games_demos, loaders_launchers, ports,
development_examples.
peripherals, games, community, media, reports: target-scoped supporting references.

Games retain platform, edition, region, language, build, patches/DLC, formats, and service
relationships separately. Projects retain upstream/revision, licenses, source references,
build requirements, and test claims. Services retain history, protocol, client dependencies,
server references, deployment requirements, and dated availability/demand observations.
Shared knowledge covers processor architectures, graphics/audio, file formats, network
protocols, cryptography references, development methods, and preservation methods.

Reference shared sources by catalog ID. Do not duplicate originals just to fill a tree.
Empty categories belong in a coverage/gap report, not a claim of missing worldwide evidence.
