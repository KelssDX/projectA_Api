using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Auditing.API.Security;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditDocumentsController : ControllerBase
    {
        private readonly IAuditDocumentsRepository _documentsRepository;
        private readonly IAuditAccessLogRepository _accessLogRepository;
        private readonly IWebHostEnvironment _environment;

        public AuditDocumentsController(
            IAuditDocumentsRepository documentsRepository,
            IAuditAccessLogRepository accessLogRepository,
            IWebHostEnvironment environment)
        {
            _documentsRepository = documentsRepository;
            _accessLogRepository = accessLogRepository;
            _environment = environment;
        }

        [HttpGet]
        [Route("GetDocument/{id}")]
        public async Task<IActionResult> GetDocument(int id)
        {
            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                var document = await _documentsRepository.GetDocumentAsync(id);
                if (document == null)
                {
                    return NotFound($"Document with ID {id} not found");
                }

                if (!CanUserAccessDocument(document, userContext))
                {
                    await TryLogDocumentAccessAsync("Metadata", document, success: false, details: "{\"reason\":\"Access denied\"}");
                    return StatusCode(403, "You do not have permission to access this document.");
                }

                await TryLogDocumentAccessAsync("Metadata", document);
                return Ok(document);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetByReference/{referenceId}")]
        public async Task<IActionResult> GetByReference(int referenceId)
        {
            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                var documents = await _documentsRepository.GetDocumentsByReferenceAsync(referenceId);
                var visibleDocuments = documents
                    .Where(document => CanUserAccessDocument(document, userContext))
                    .ToList();

                var hiddenCount = Math.Max(0, documents.Count - visibleDocuments.Count);
                foreach (var document in visibleDocuments)
                {
                    await TryLogDocumentAccessAsync(
                        "List",
                        document,
                        details: JsonSerializer.Serialize(new
                        {
                            ReferenceId = referenceId,
                            VisibleDocumentCount = visibleDocuments.Count,
                            HiddenDocumentCount = hiddenCount
                        }));
                }

                return Ok(visibleDocuments);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetCategories")]
        public async Task<IActionResult> GetCategories()
        {
            try
            {
                var categories = await _documentsRepository.GetDocumentCategoriesAsync();
                return Ok(categories);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetVisibilityOptions")]
        public async Task<IActionResult> GetVisibilityOptions()
        {
            try
            {
                var visibilityOptions = await _documentsRepository.GetDocumentVisibilityOptionsAsync();
                return Ok(visibilityOptions);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetAccessLogsByReference/{referenceId}")]
        public async Task<IActionResult> GetAccessLogsByReference(int referenceId, [FromQuery] int? documentId = null, [FromQuery] int limit = 25)
        {
            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                if (!userContext.CanManageDocumentSecurity())
                {
                    return StatusCode(403, "You do not have permission to view document access activity.");
                }

                var normalizedLimit = limit <= 0 ? 25 : Math.Min(limit, 200);
                var logs = await _accessLogRepository.GetDocumentAccessLogsByReferenceAsync(referenceId, documentId, normalizedLimit);
                return Ok(logs);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetEvidenceRequestsByReference/{referenceId}")]
        public async Task<IActionResult> GetEvidenceRequestsByReference(int referenceId)
        {
            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                var requests = await _documentsRepository.GetEvidenceRequestsByReferenceAsync(referenceId);
                if (IsClientEvidenceContributor(userContext))
                {
                    requests = requests
                        .Where(request => IsEvidenceRequestAssignedToUser(request, userContext))
                        .ToList();
                }

                await RedactRestrictedDocumentLinksAsync(requests, userContext);
                return Ok(requests);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetEvidenceRequestStatuses")]
        public async Task<IActionResult> GetEvidenceRequestStatuses()
        {
            try
            {
                var statuses = await _documentsRepository.GetEvidenceRequestStatusesAsync();
                return Ok(statuses);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("CreateEvidenceRequest")]
        public async Task<IActionResult> CreateEvidenceRequest([FromBody] CreateAuditEvidenceRequestRequest request)
        {
            if (request.ReferenceId <= 0 || string.IsNullOrWhiteSpace(request.Title))
            {
                return BadRequest("Reference ID and title are required");
            }

            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                if (!userContext.CanReviewAuditContent())
                {
                    return StatusCode(403, "You do not have permission to create evidence requests.");
                }

                var created = await _documentsRepository.CreateEvidenceRequestAsync(request);
                return CreatedAtAction(nameof(GetEvidenceRequestsByReference), new { referenceId = created.ReferenceId }, created);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("ReviewEvidenceRequestItem")]
        public async Task<IActionResult> ReviewEvidenceRequestItem([FromBody] ReviewEvidenceRequestItemRequest request)
        {
            if (request.RequestItemId <= 0)
            {
                return BadRequest("Evidence request item is required");
            }

            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                if (!userContext.CanReviewAuditContent())
                {
                    return StatusCode(403, "You do not have permission to review evidence request items.");
                }

                var reviewed = await _documentsRepository.ReviewEvidenceRequestItemAsync(request);
                return Ok(reviewed);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("UploadDocument")]
        [RequestFormLimits(MultipartBodyLengthLimit = 104857600)]
        [RequestSizeLimit(104857600)]
        public async Task<IActionResult> UploadDocument([FromForm] UploadAuditDocumentForm request)
        {
            if (request.ReferenceId <= 0 || request.File == null || request.File.Length == 0)
            {
                return BadRequest("Reference ID and file are required");
            }

            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.CanSubmitEvidence())
            {
                return StatusCode(403, "You do not have permission to upload audit documents.");
            }

            var requestedCategory = await ResolveRequestedCategoryAsync(request.CategoryId);
            var requestedGrantedUserIds = ParseCsvIntValues(request.GrantedUserIdsCsv);
            var requestedGrantedRoleNames = ParseCsvStringValues(request.GrantedRoleNamesCsv);
            var requestedVisibilityId = request.VisibilityLevelId ?? requestedCategory?.DefaultVisibilityLevelId;
            var requestedVisibility = await ResolveRequestedVisibilityOptionAsync(requestedVisibilityId);
            var effectiveConfidentialityLabel = string.IsNullOrWhiteSpace(request.ConfidentialityLabel)
                ? requestedCategory?.DefaultConfidentialityLabel
                : request.ConfidentialityLabel?.Trim();
            var requiresSecurityApproval = (requestedCategory?.RequiresSecurityApproval ?? false)
                || (requestedVisibility?.IsRestricted ?? false);
            if (requiresSecurityApproval)
            {
                if (string.IsNullOrWhiteSpace(effectiveConfidentialityLabel) || string.IsNullOrWhiteSpace(request.ConfidentialityReason))
                {
                    return BadRequest("Restricted visibility requires both a confidentiality label and confidentiality reason.");
                }

                if (NormalizeValue(requestedVisibility?.Name) == "restricted"
                    && requestedGrantedUserIds.Count == 0
                    && requestedGrantedRoleNames.Count == 0
                    && !userContext.CanManageDocumentSecurity())
                {
                    return BadRequest("Restricted documents require at least one explicit user or role grant, or a document security manager.");
                }
            }

            if (IsClientEvidenceContributor(userContext))
            {
                if (!request.RequestItemId.HasValue || request.RequestItemId.Value <= 0)
                {
                    return StatusCode(403, "Client contributors may only upload evidence against assigned request items.");
                }

                var assignment = await _documentsRepository.GetEvidenceRequestAssignmentContextByItemAsync(request.RequestItemId.Value);
                if (assignment == null || assignment.ReferenceId != request.ReferenceId)
                {
                    return StatusCode(403, "The selected evidence request item is not valid for this audit file.");
                }

                if (!IsEvidenceRequestAssignedToUser(assignment, userContext))
                {
                    return StatusCode(403, "You do not have permission to upload against this evidence request.");
                }

                if (assignment.FulfilledDocumentId.HasValue)
                {
                    return Conflict("This evidence request item has already been fulfilled.");
                }
            }

            var originalFileName = Path.GetFileName(request.File.FileName);
            var extension = Path.GetExtension(originalFileName);
            var storedFileName = $"{DateTime.UtcNow:yyyyMMddHHmmssfff}_{Guid.NewGuid():N}{extension}";
            var referenceFolder = request.ReferenceId.GetValueOrDefault().ToString();
            var relativeFolder = Path.Combine("uploads", "audit-documents", referenceFolder);
            var fullFolder = Path.Combine(_environment.ContentRootPath, relativeFolder);
            Directory.CreateDirectory(fullFolder);

            var fullPath = Path.Combine(fullFolder, storedFileName);
            try
            {
                var securityReviewStatus = requiresSecurityApproval
                    ? (userContext.CanManageDocumentSecurity() ? "Approved" : "Pending Approval")
                    : "Not Required";

                await using (var stream = System.IO.File.Create(fullPath))
                {
                    await request.File.CopyToAsync(stream);
                }

                var createRequest = new CreateAuditDocumentRequest
                {
                    ReferenceId = request.ReferenceId,
                    AuditUniverseId = request.AuditUniverseId,
                    ProcedureId = request.ProcedureId,
                    WorkingPaperId = request.WorkingPaperId,
                    FindingId = request.FindingId,
                    RecommendationId = request.RecommendationId,
                    Title = string.IsNullOrWhiteSpace(request.Title) ? Path.GetFileNameWithoutExtension(originalFileName) : request.Title.Trim(),
                    OriginalFileName = originalFileName,
                    StoredFileName = storedFileName,
                    StoredRelativePath = Path.Combine(relativeFolder, storedFileName).Replace("\\", "/"),
                    ContentType = string.IsNullOrWhiteSpace(request.File.ContentType) ? "application/octet-stream" : request.File.ContentType,
                    FileExtension = extension,
                    FileSize = request.File.Length,
                    CategoryId = request.CategoryId,
                    VisibilityLevelId = requestedVisibilityId,
                    SourceType = string.IsNullOrWhiteSpace(request.SourceType) ? "Audit Team" : request.SourceType.Trim(),
                    Tags = request.Tags,
                    Notes = request.Notes,
                    ConfidentialityLabel = effectiveConfidentialityLabel,
                    ConfidentialityReason = request.ConfidentialityReason,
                    SecurityReviewRequired = requiresSecurityApproval,
                    SecurityReviewStatus = securityReviewStatus,
                    SecurityReviewRequestedAt = requiresSecurityApproval && !userContext.CanManageDocumentSecurity() ? DateTime.UtcNow : null,
                    SecurityReviewRequestedByUserId = requiresSecurityApproval && !userContext.CanManageDocumentSecurity() ? userContext.UserId : null,
                    SecurityReviewRequestedByName = requiresSecurityApproval && !userContext.CanManageDocumentSecurity() ? userContext.GetDisplayName("Audit User") : null,
                    SecurityReviewedAt = requiresSecurityApproval && userContext.CanManageDocumentSecurity() ? DateTime.UtcNow : null,
                    SecurityReviewedByUserId = requiresSecurityApproval && userContext.CanManageDocumentSecurity() ? userContext.UserId : null,
                    SecurityReviewedByName = requiresSecurityApproval && userContext.CanManageDocumentSecurity() ? userContext.GetDisplayName("Audit User") : null,
                    SecurityReviewNotes = requiresSecurityApproval && userContext.CanManageDocumentSecurity() ? "Auto-approved by document security manager during upload." : null,
                    UploadedByName = string.IsNullOrWhiteSpace(request.UploadedByName)
                        ? userContext.GetDisplayName("Audit User")
                        : request.UploadedByName,
                    UploadedByUserId = request.UploadedByUserId ?? userContext.UserId,
                    GrantedByName = userContext.GetDisplayName("Audit User"),
                    GrantedByUserId = userContext.UserId,
                    GrantedUserIds = requestedGrantedUserIds,
                    GrantedRoleNames = requestedGrantedRoleNames
                };

                var created = await _documentsRepository.CreateDocumentAsync(createRequest);

                if (request.RequestItemId.HasValue && request.RequestItemId.Value > 0)
                {
                    await _documentsRepository.FulfillEvidenceRequestItemAsync(request.RequestItemId.Value, created.Id);
                }

                await TryLogDocumentAccessAsync(
                    "Upload",
                    created,
                    details: JsonSerializer.Serialize(new
                    {
                        created.CategoryId,
                        created.VisibilityLevelId,
                        created.VisibilityLevelName,
                        created.ProcedureId,
                        created.WorkingPaperId,
                        created.FindingId,
                        created.RecommendationId,
                        created.ConfidentialityLabel
                        }));

                if (createRequest.HasExplicitGrants)
                {
                    await TryLogDocumentAccessAsync(
                        "PermissionGrant",
                        created,
                        details: JsonSerializer.Serialize(new
                        {
                            created.VisibilityLevelName,
                            GrantedUserIds = createRequest.GrantedUserIds,
                            GrantedRoleNames = createRequest.GrantedRoleNames,
                            created.ConfidentialityLabel,
                            created.ConfidentialityReason
                        }));
                }

                if (requiresSecurityApproval && !userContext.CanManageDocumentSecurity())
                {
                    await TryLogDocumentAccessAsync(
                        "SecurityReviewRequested",
                        created,
                        details: JsonSerializer.Serialize(new
                        {
                            created.CategoryName,
                            created.VisibilityLevelName,
                            created.ConfidentialityLabel,
                            created.SecurityReviewStatus
                        }));
                }

                return CreatedAtAction(nameof(GetDocument), new { id = created.Id }, created);
            }
            catch (Exception ex)
            {
                if (System.IO.File.Exists(fullPath))
                {
                    try
                    {
                        System.IO.File.Delete(fullPath);
                    }
                    catch
                    {
                        // Best effort cleanup only.
                    }
                }

                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut]
        [Route("UpdateDocumentSecurity/{id}")]
        public async Task<IActionResult> UpdateDocumentSecurity(int id, [FromBody] UpdateAuditDocumentSecurityRequest request)
        {
            if (id <= 0 || request == null)
            {
                return BadRequest("Document ID and security payload are required.");
            }

            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                var document = await _documentsRepository.GetDocumentAsync(id);
                if (document == null)
                {
                    return NotFound($"Document with ID {id} not found");
                }

                if (!CanUserUpdateDocumentSecurity(document, userContext))
                {
                    await TryLogDocumentAccessAsync("PermissionChange", document, success: false, details: "{\"reason\":\"Permission change denied\"}");
                    return StatusCode(403, "You do not have permission to update document security.");
                }

                var requestedVisibility = await ResolveRequestedVisibilityOptionAsync(request.VisibilityLevelId);
                if (requestedVisibility?.IsRestricted == true
                    && (string.IsNullOrWhiteSpace(request.ConfidentialityLabel) || string.IsNullOrWhiteSpace(request.ConfidentialityReason)))
                {
                    return BadRequest("Restricted visibility requires both a confidentiality label and confidentiality reason.");
                }

                request.UpdatedByName = string.IsNullOrWhiteSpace(request.UpdatedByName)
                    ? userContext.GetDisplayName("Audit User")
                    : request.UpdatedByName.Trim();
                request.UpdatedByUserId ??= userContext.UserId;

                var updated = await _documentsRepository.UpdateDocumentSecurityAsync(id, request);
                await TryLogDocumentAccessAsync(
                    "PermissionChange",
                    updated,
                    details: JsonSerializer.Serialize(new
                    {
                        Before = new
                        {
                            document.VisibilityLevelName,
                            document.ConfidentialityLabel,
                            document.ConfidentialityReason,
                            document.AccessSummary,
                            Grants = document.AccessGrants?.Select(grant => new
                            {
                                grant.GranteeUserId,
                                grant.GranteeRoleName,
                                grant.PermissionLevel,
                                grant.CanDownload
                            })
                        },
                        After = new
                        {
                            updated.VisibilityLevelName,
                            updated.ConfidentialityLabel,
                            updated.ConfidentialityReason,
                            updated.AccessSummary,
                            Grants = updated.AccessGrants?.Select(grant => new
                            {
                                grant.GranteeUserId,
                                grant.GranteeRoleName,
                                grant.PermissionLevel,
                                grant.CanDownload
                            })
                        }
                    }));

                return Ok(updated);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("ReviewDocumentSecurity/{id}")]
        public async Task<IActionResult> ReviewDocumentSecurity(int id, [FromBody] ReviewAuditDocumentSecurityRequest request)
        {
            if (id <= 0 || request == null)
            {
                return BadRequest("Document ID and review payload are required.");
            }

            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                if (!userContext.CanManageDocumentSecurity())
                {
                    return StatusCode(403, "You do not have permission to review document security.");
                }

                var document = await _documentsRepository.GetDocumentAsync(id);
                if (document == null)
                {
                    return NotFound($"Document with ID {id} not found");
                }

                request.ReviewedByUserId ??= userContext.UserId;
                request.ReviewedByName = string.IsNullOrWhiteSpace(request.ReviewedByName)
                    ? userContext.GetDisplayName("Audit User")
                    : request.ReviewedByName.Trim();

                var reviewed = await _documentsRepository.ReviewDocumentSecurityAsync(id, request);
                await TryLogDocumentAccessAsync(
                    "SecurityReview",
                    reviewed,
                    details: JsonSerializer.Serialize(new
                    {
                        reviewed.SecurityReviewStatus,
                        request.ReviewNotes,
                        request.ReviewedByName
                    }));

                return Ok(reviewed);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("DownloadDocument/{id}")]
        public async Task<IActionResult> DownloadDocument(int id)
        {
            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                var document = await _documentsRepository.GetDocumentAsync(id);
                if (document == null)
                {
                    return NotFound($"Document with ID {id} not found");
                }

                if (!CanUserAccessDocument(document, userContext))
                {
                    await TryLogDocumentAccessAsync("Download", document, success: false, details: "{\"reason\":\"Access denied\"}");
                    return StatusCode(403, "You do not have permission to download this document.");
                }

                var fullPath = ResolveDocumentPath(document.StoredRelativePath);
                if (!System.IO.File.Exists(fullPath))
                {
                    await TryLogDocumentAccessAsync("Download", document, success: false, details: "{\"reason\":\"Stored file not found\"}");
                    return NotFound("Stored file not found");
                }

                await TryLogDocumentAccessAsync("Download", document);
                return PhysicalFile(fullPath, document.ContentType ?? "application/octet-stream", document.OriginalFileName ?? document.StoredFileName);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete]
        [Route("DeleteDocument/{id}")]
        public async Task<IActionResult> DeleteDocument(int id)
        {
            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                var document = await _documentsRepository.GetDocumentAsync(id);
                if (document == null)
                {
                    return NotFound($"Document with ID {id} not found");
                }

                if (!CanUserManageDocument(document, userContext))
                {
                    await TryLogDocumentAccessAsync("Delete", document, success: false, details: "{\"reason\":\"Delete denied\"}");
                    return StatusCode(403, "You do not have permission to delete this document.");
                }

                var deleted = await _documentsRepository.DeleteDocumentAsync(id);
                if (!deleted)
                {
                    return NotFound($"Document with ID {id} not found");
                }

                var fullPath = ResolveDocumentPath(document.StoredRelativePath);
                if (System.IO.File.Exists(fullPath))
                {
                    try
                    {
                        System.IO.File.Delete(fullPath);
                    }
                    catch
                    {
                        // Keep the API operation successful even if file cleanup is delayed.
                    }
                }

                await TryLogDocumentAccessAsync("Delete", document);

                return Ok(new { message = "Document deleted successfully", id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        private static bool IsClientEvidenceContributor(AuditApiUserContext userContext)
            => userContext != null && userContext.CanSubmitEvidence() && !userContext.IsAuditTeamMember();

        private static bool IsEvidenceRequestAssignedToUser(AuditEvidenceRequest request, AuditApiUserContext userContext)
        {
            return request != null && IsEvidenceRequestAssignedToUser(
                request.RequestedToEmail,
                userContext);
        }

        private static bool IsEvidenceRequestAssignedToUser(AuditEvidenceRequestAssignmentContext request, AuditApiUserContext userContext)
        {
            return request != null && IsEvidenceRequestAssignedToUser(
                request.RequestedToEmail,
                userContext);
        }

        private static bool IsEvidenceRequestAssignedToUser(string requestedToEmail, AuditApiUserContext userContext)
        {
            var normalizedRequestedTo = NormalizeEmail(requestedToEmail);
            if (string.IsNullOrWhiteSpace(normalizedRequestedTo))
            {
                return false;
            }

            var userCandidates = new[]
            {
                NormalizeEmail(userContext?.UserEmail),
                NormalizeEmail(userContext?.UserName)
            }
            .Where(value => !string.IsNullOrWhiteSpace(value))
            .Distinct(StringComparer.OrdinalIgnoreCase);

            return userCandidates.Contains(normalizedRequestedTo, StringComparer.OrdinalIgnoreCase);
        }

        private async Task RedactRestrictedDocumentLinksAsync(
            System.Collections.Generic.IEnumerable<AuditEvidenceRequest> requests,
            AuditApiUserContext userContext)
        {
            if (requests == null)
            {
                return;
            }

            var documentCache = new Dictionary<int, AuditDocument?>();

            foreach (var request in requests)
            {
                if (request?.Items == null)
                {
                    continue;
                }

                foreach (var item in request.Items)
                {
                    if (!item.FulfilledDocumentId.HasValue || item.FulfilledDocumentId.Value <= 0)
                    {
                        continue;
                    }

                    if (!documentCache.TryGetValue(item.FulfilledDocumentId.Value, out var document))
                    {
                        document = await _documentsRepository.GetDocumentAsync(item.FulfilledDocumentId.Value);
                        documentCache[item.FulfilledDocumentId.Value] = document;
                    }

                    if (document == null || CanUserAccessDocument(document, userContext))
                    {
                        continue;
                    }

                    item.FulfilledDocumentCode = "Restricted";
                    item.FulfilledDocumentTitle = "Restricted document";
                }
            }
        }

        private bool CanUserAccessDocument(AuditDocument document, AuditApiUserContext userContext)
        {
            if (document == null || !document.IsActive)
            {
                return false;
            }

            if (RequiresSecurityReviewDecision(document))
            {
                return userContext.CanManageDocumentSecurity() || IsDocumentUploader(document, userContext);
            }

            if (userContext.CanManageDocumentSecurity())
            {
                return true;
            }

            if (IsDocumentUploader(document, userContext))
            {
                return true;
            }

            if (HasExplicitDocumentGrant(document, userContext))
            {
                return true;
            }

            var visibility = NormalizeValue(document.VisibilityLevelName);
            if (string.IsNullOrWhiteSpace(visibility) || visibility == "engagement_team")
            {
                return userContext.IsAuditTeamMember();
            }

            return visibility switch
            {
                "managers_and_reviewers" => userContext.CanAccessManagerReviewOnlyContent(),
                "private_draft" => false,
                "restricted" => false,
                _ => userContext.IsAuditTeamMember()
            };
        }

        private bool CanUserManageDocument(AuditDocument document, AuditApiUserContext userContext)
        {
            if (document == null)
            {
                return false;
            }

            if (userContext.CanManageAuditContent())
            {
                return true;
            }

            if (IsDocumentUploader(document, userContext))
            {
                return true;
            }

            return HasExplicitDocumentGrant(document, userContext, requiredPermission: "manage");
        }

        private bool CanUserUpdateDocumentSecurity(AuditDocument document, AuditApiUserContext userContext)
        {
            if (document == null)
            {
                return false;
            }

            if (userContext.CanManageDocumentSecurity())
            {
                return true;
            }

            return HasExplicitDocumentGrant(document, userContext, requiredPermission: "manage");
        }

        private static bool RequiresSecurityReviewDecision(AuditDocument document)
        {
            if (document == null || !document.SecurityReviewRequired)
            {
                return false;
            }

            var normalizedStatus = NormalizeValue(document.SecurityReviewStatus);
            return normalizedStatus != "approved" && normalizedStatus != "not_required";
        }

        private static bool IsDocumentUploader(AuditDocument document, AuditApiUserContext userContext)
        {
            if (document == null || userContext == null)
            {
                return false;
            }

            if (userContext.UserId.HasValue && document.UploadedByUserId.HasValue)
            {
                return userContext.UserId.Value == document.UploadedByUserId.Value;
            }

            return !string.IsNullOrWhiteSpace(userContext.UserName)
                && !string.IsNullOrWhiteSpace(document.UploadedByName)
                && string.Equals(userContext.UserName.Trim(), document.UploadedByName.Trim(), StringComparison.OrdinalIgnoreCase);
        }

        private static bool HasExplicitDocumentGrant(
            AuditDocument document,
            AuditApiUserContext userContext,
            string requiredPermission = "view")
        {
            var required = NormalizeValue(requiredPermission);
            foreach (var grant in document?.AccessGrants ?? Enumerable.Empty<AuditDocumentAccessGrant>())
            {
                var permission = NormalizeValue(grant.PermissionLevel);
                var permissionMatches = permission == required || (required == "view" && permission == "manage");
                if (!permissionMatches)
                {
                    continue;
                }

                if (grant.GranteeUserId.HasValue && userContext.UserId.HasValue && grant.GranteeUserId.Value == userContext.UserId.Value)
                {
                    return true;
                }

                if (!string.IsNullOrWhiteSpace(grant.GranteeRoleName) && userContext.HasNormalizedRole(grant.GranteeRoleName))
                {
                    return true;
                }
            }

            return false;
        }

        private static List<int> ParseCsvIntValues(string? csv)
        {
            return (csv ?? string.Empty)
                .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                .Select(value => int.TryParse(value, out var parsed) ? parsed : (int?)null)
                .Where(value => value.HasValue && value.Value > 0)
                .Select(value => value!.Value)
                .Distinct()
                .ToList();
        }

        private static List<string> ParseCsvStringValues(string? csv)
        {
            return (csv ?? string.Empty)
                .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                .Where(value => !string.IsNullOrWhiteSpace(value))
                .Select(value => value.Trim())
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();
        }

        private static string NormalizeValue(string? value)
            => (value ?? string.Empty).Trim().ToLowerInvariant().Replace("-", "_").Replace(" ", "_");

        private static string NormalizeEmail(string? value)
            => (value ?? string.Empty).Trim().ToLowerInvariant();

        private string ResolveDocumentPath(string storedRelativePath)
        {
            var normalized = (storedRelativePath ?? string.Empty).Replace("/", Path.DirectorySeparatorChar.ToString());
            return Path.Combine(_environment.ContentRootPath, normalized);
        }

        private async Task<AuditDocumentVisibilityOption?> ResolveRequestedVisibilityOptionAsync(int? visibilityLevelId)
        {
            if (!visibilityLevelId.HasValue || visibilityLevelId.Value <= 0)
            {
                return null;
            }

            var visibilityOptions = await _documentsRepository.GetDocumentVisibilityOptionsAsync();
            return visibilityOptions?.FirstOrDefault(option => option.Id == visibilityLevelId.Value);
        }

        private async Task<AuditDocumentCategory?> ResolveRequestedCategoryAsync(int? categoryId)
        {
            if (!categoryId.HasValue || categoryId.Value <= 0)
            {
                return null;
            }

            var categories = await _documentsRepository.GetDocumentCategoriesAsync();
            return categories?.FirstOrDefault(category => category.Id == categoryId.Value);
        }

        private async Task TryLogDocumentAccessAsync(string actionType, AuditDocument document, bool success = true, string? details = null)
        {
            if (document == null || document.Id <= 0)
            {
                return;
            }

            try
            {
                var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
                await _accessLogRepository.LogDocumentAccessAsync(new AuditDocumentAccessLogEntry
                {
                    DocumentId = document.Id,
                    ReferenceId = document.ReferenceId,
                    ActionType = actionType,
                    AccessedByUserId = userContext.UserId,
                    AccessedByName = userContext.GetDisplayName("Audit User"),
                    IpAddress = HttpContext?.Connection?.RemoteIpAddress?.ToString(),
                    ClientContext = Request?.Headers?.UserAgent.ToString(),
                    CorrelationId = HttpContext?.TraceIdentifier,
                    Success = success,
                    DetailsJson = details
                });
            }
            catch
            {
                // Access logging is best effort and must not fail the document operation.
            }
        }
    }

    public class UploadAuditDocumentForm
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public int? ProcedureId { get; set; }
        public int? WorkingPaperId { get; set; }
        public int? FindingId { get; set; }
        public int? RecommendationId { get; set; }
        public int? CategoryId { get; set; }
        public int? RequestItemId { get; set; }
        public int? VisibilityLevelId { get; set; }
        public string? Title { get; set; }
        public string? SourceType { get; set; }
        public string? Tags { get; set; }
        public string? Notes { get; set; }
        public string? ConfidentialityLabel { get; set; }
        public string? ConfidentialityReason { get; set; }
        public string? GrantedUserIdsCsv { get; set; }
        public string? GrantedRoleNamesCsv { get; set; }
        public string? UploadedByName { get; set; }
        public int? UploadedByUserId { get; set; }
        public Microsoft.AspNetCore.Http.IFormFile? File { get; set; }
    }
}
